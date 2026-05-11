# Code Review — Forum Backend

**Reviewer's note:** This is a junior intern project. The review is direct because that's what learning needs — each finding includes the *why* and a fix. The work shows real progress (clean layering, async stack, pagination, rate-limit middleware, auth scaffolding, decent tests for happy paths). The issues below are normal for someone learning; treat the **Critical** items as must-fix learning moments.

---

## Scope Gap (read this first)

The spec calls for **FastAPI backend AND a React + TypeScript + Tailwind frontend** plus Week-3 polish (search/filter, profile edit, frontend tests). What's delivered is **backend only**. Roughly half the spec is unbuilt:

- No `frontend/` directory at all
- No search/filter endpoint
- No profile edit
- No global error handler / structured error envelope
- No CORS middleware (the frontend, when built, will not be able to call the API)

Either the scope was renegotiated to "backend only" (fine — say so in the README) or the second half is still to do.

---

## Critical (must fix before merge)

### 1. Refresh tokens stored in plaintext
`forum/backend/src/routes/auth.py:88-100` sets `token_hash=token_str` — the raw URL-safe token is written to the column literally named `token_hash`. Anyone with read access to the DB (or a leaked backup) can use those tokens to mint new access tokens.

The codebase already has a correct hashing helper at `core/auth/refresh_tokens.py:22-23` (`hash_refresh_token = sha256(...).hexdigest()`) — it's just unused.

**Fix:** in `auth.py:create_refresh_tokens`, store `hash_refresh_token(token_str)` and return the plain `token_str` to the caller. Look it up the same way on rotation/revoke.

### 2. `core/auth/refresh_tokens.py` is dead AND broken
The file is never imported. If it ever is, it will crash: it uses sync `db.query(...)` (`refresh_tokens.py:39, 61`) against the project's `AsyncSession`. The whole file looks like an earlier draft that got abandoned.

**Fix:** either rewrite it with `await db.execute(select(...))` and route `auth.py` through it (preferred — the rotation/revoke logic there is the *correct* design), or delete it. Don't leave two implementations of the same concept.

### 3. No `/refresh` or `/logout` endpoint
Refresh tokens are issued at `/auth/token` but there's no endpoint to consume one for a new access token, and no way to revoke. So the entire refresh-token table is write-only — useless. JWT access tokens expire in 15 minutes (`settings.py:32`), so users will silently log out every 15 min with no recovery.

**Fix:** add `POST /api/auth/refresh` (rotate + return new pair) and `POST /api/auth/logout` (revoke). Use the rotation logic in `core/auth/refresh_tokens.py` once it's de-broken.

### 4. Per-module `Limiter` instances do nothing
`routes/auth.py:19`, `routes/posts.py:6`, `routes/comments.py:14`, `routes/users.py:13` each instantiate a brand-new `Limiter`. The `@limiter.limit("10/minute")` decorators on register/login (`auth.py:47, 70`) reference *those* limiters, but the FastAPI app only knows about the one in `app.py:9`. Decorator-based per-route limits in slowapi require the same `Limiter` instance that's registered on `app.state.limiter`.

Result: the strict 10/min on `/register` and `/login` is not enforced. Only the global 80/min middleware applies. This is a brute-force exposure.

**Fix:** create one shared limiter (e.g. `core/rate_limit.py`) and import it everywhere. Remove the unused per-module `Limiter()` calls.

### 5. CORS is not configured
There's no `CORSMiddleware`. The spec lists CORS as a learning outcome and the frontend will require it. Add it, and read allowed origins from settings — never `["*"]` once cookies/auth are involved.

### 6. Unbounded eager-load on every authenticated request
`models/user.py:32-53` declares `posts`, `comments`, `refresh_tokens` all with `lazy="selectin"`. `core/auth/dependencies.py:32-33` runs on **every** authenticated request and loads the User. SQLAlchemy will then issue 3 extra `SELECT … WHERE user_id = ?` queries that pull every row the user has ever produced. A power user with thousands of comments and refresh tokens will pay for them on every API call.

**Fix:** drop `lazy="selectin"` from these relationships (default `lazy="select"` is fine). Pass `selectinload(User.posts)` *explicitly* in the one place that needs it (`get_user_profile`). Same treatment for `Post.comments`/`Post.owner` and `Comment.author`/`Comment.post` — eager-load at the *query* site, never at the model.

---

## Important (should fix)

### 7. Login by email but the field is named `username`
`services/user_service.py:66-76`: `authenticate_user(db, email, password)` is fed `OAuth2PasswordRequestForm.username` from `routes/auth.py:77`. The form field is called `username`, the function calls it `email`, and `get_user_by_email` runs the lookup. Meanwhile JWT `sub` is `user.username`. This is the kind of confusion that produces an auth bug six months from now.

**Fix:** pick one identifier, document it. If you want either, do `select(User).where(or_(User.email==x, User.username==x))` and rename the parameter to `identifier`.

### 8. `update_post` partial-update logic conflates empty string with "not provided"
`services/post_service.py:88-91`:
```python
if post_update.title:
    db_post.title = post_update.title
```
An explicit empty string is silently ignored — user can't blank a field, and you can't tell "field omitted" from "field set to empty". Also the route declares `response_model=ApiResponse[PostUpdate]` (`routes/posts.py:39`) which strips id/created_at/comments_count from the response.

**Fix:** `for k, v in post_update.model_dump(exclude_unset=True).items(): setattr(db_post, k, v)`. Change the response model to `PostResponse`. Add `min_length`/`max_length` to `PostCreate.title`/`content` (see also #11).

### 9. Inconsistent service return shapes
Compare:
- `post_service.create_new_post` → returns the ORM `Post`; the route wraps it in `ApiResponse`.
- `comment_service.comment_create` → returns `ApiResponse[CommentResponse]` already; the route returns it directly.
- `comment_service.delete_post_comment` → returns `ApiResponse[None]`; route returns it directly.
- `post_service.delete_post` → returns `True`; route wraps it.

Pick one rule: **services return domain objects, routes wrap them.** The current mix forces every reader to check both layers to know what they get back.

### 10. Missing dependency for the configured async driver
`pyproject.toml:19` declares `psycopg[binary]` but `core/db_connection/database.py:9-10` rewrites the URL to `postgresql+asyncpg://`. The first prod boot will fail with `ModuleNotFoundError: asyncpg`. Either add `asyncpg` to dependencies or use `postgresql+psycopg://` (psycopg 3 supports async).

### 11. Validation is thinner than the spec asks for
The spec's Week-3 item is "Comprehensive Pydantic validation". Today:
- `PostCreate` (`schemas/posts.py:7-9`) has no length limits on title/content. The `Post.title` column is `String(200)` so a 201-char title triggers a DB error instead of a 422.
- `CommentCreate.content` and `CommentUpdate.content` have no `min_length=1` — empty comments accepted.
- `UserCreate.password` has length, but no complexity rule (any 8 lowercase letters works).

### 12. `get_user_by_id` does not return user posts
Spec Week 3: "User profile endpoint with user's posts". `routes/users.py:25` returns just `UserResponse`. `/users/me` returns posts; `/users/{id}` doesn't. Two endpoints, two contracts for the same concept.

### 13. README is wrong about env vars
`README.md:80-85` shows `SECRET_KEY` / `ALGORITHM=HS256` / `DATABASE_URL`. Actual settings (`src/config/settings.py`) require `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY` (RS256), `APP_ENV`, `POSTGRES_URL`, `SQLITE_DATABASE_URL`. A reviewer following the README cannot start the app.

### 14. Tests assert too little — including one false positive
- `tests/api/test_post.py:52-58` `test_get_posts` doesn't pull in `test_posts`, so the DB is empty. It then asserts `len(result.json()["data"]) == 2`. `data` is the paginated dict `{"items": [...], "meta": {...}}` — `len(dict) == 2` always. The assertion passes for the wrong reason. Replace with `assert len(body["data"]["items"]) == 0` (or fix the fixture wiring and assert 3).
- No 401 (missing token), 403 (other user's post), 404 (missing id), or 422 (validation) tests anywhere. Coverage is happy-path only — every authorization rule in `post_service`/`comment_service` is untested. Add at least one negative test per rule.
- `test_register` doesn't verify the password is hashed (not stored plain).

### 15. `Settings` typo-aliasing hides misconfiguration
`settings.py:27` accepts `POSTGRESS_URL`/`POTGRESS_URL`; `:48-61` maps `devlop`/`developement`/`pod` to canonical values. Cute, but a deployer who typed `POTGRESS_URL` will be perplexed when somebody else "fixes the typo" and the wrong env var is read in prod. Fail loudly on unknown values.

---

## Suggestions / Nits

- `update_post` (`post_service.py:73-95`) does two queries when it could do one — `db.get(Post, post_id)` is enough.
- `comment_service.delete_post_comment` and `update_post_comment` parameter order is inconsistent (`comment_id, comment_data, user_id` vs `comment_data, comment_id, user_id`). Pick a convention.
- `Post.updated_at` has `server_default` but `User.updated_at` doesn't (`models/user.py:28-30`) — first insert leaves it `NULL`. Add `server_default=func.now()` for symmetry with the spec schema.
- `routes/comments.py:25` mutates `comment.post_id = id` before passing on. Cleaner: don't put `post_id` in `CommentCreate` at all, and have the service take `post_id` as a separate arg. The path is the source of truth.
- `routes/posts.py:6` and `comments.py:14` create `limiter = Limiter(...)` but never use it after #4 is fixed — delete.
- Trailing whitespace and odd spacing in route signatures (`routes/comments.py:17`, `routes/auth.py:7,15`). Run `ruff format` (already a dependency).
- `tests/conftest.py:41-45`: `expire_on_commit=False` on the test session is good; but `await session.rollback()` after the test won't undo committed changes — the per-test schema drop+create on `engine.begin()` is what isolates tests. Worth a one-line comment so future-you doesn't move the rollback to "fix" something.
- `app.py:23-25` health endpoint is exempt from the rate limiter (good for k8s probes) but advertises `/api/auth/register` as a "test_endpoint" — drop that, it's noise.
- `.idea/` is checked in (top-level). Add to `.gitignore` and `git rm -r --cached .idea`.

---

## Verdict

**Request changes.** The architecture and layering are solid for a junior — that part is genuinely good work. But the auth path has a real security bug (#1), a dead/broken parallel implementation (#2), an incomplete contract (#3), and rate limits that don't fire (#4); plus the eager-load pattern (#6) will make every authenticated request progressively slower. None of these are hard to fix, and fixing them is the highest-leverage learning in this project.

**Recommended order to tackle:** #1 → #2 → #3 (one PR, refresh-token correctness) → #4 + #5 (one PR, middleware) → #6 + #9 (one PR, query hygiene) → #7, #8, #11, #12 (correctness polish) → #13, #14 (docs + tests) → frontend work.
