import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import app
from core.auth.password import hash_password
from core.db_connection.database import Base
from core.db_connection.session import get_db
from src.models.comments import Comment
from src.models.posts import Post
from src.models.user import User


# =========================
# ENGINE
# =========================
@pytest_asyncio.fixture(scope="session")
def engine():
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )


# =========================
# DB SESSION
# =========================
@pytest_asyncio.fixture
async def db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with SessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()


# =========================
# CLIENT (FastAPI override DB)
# =========================
@pytest_asyncio.fixture
async def client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
            transport=transport,
            base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# =========================
# SINGLE AUTH USER (IMPORTANT)
# =========================
@pytest_asyncio.fixture
async def auth_user(db):
    user = User(
        username="tester",
        email="test@test.com",
        password_hash=hash_password("password123"),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# =========================
# AUTH HEADERS
# =========================

@pytest_asyncio.fixture
async def auth_headers(client, auth_user):
    response = await client.post(
        "/api/auth/token",
        data={
            "grant_type": "password",
            "username": auth_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_posts(db, auth_user):
    post1 = Post(title="Post 1", content="Content 1", user_id=auth_user.id)
    post2 = Post(title="Post 2", content="Content 2", user_id=auth_user.id)
    post3 = Post(title="Post 3", content="Content 3", user_id=auth_user.id)

    db.add_all([post1, post2, post3])
    await db.commit()

    for p in (post1, post2, post3):
        await db.refresh(p)

    return post1, post2, post3


# =========================
# COMMENTS (SAME USER CONSISTENCY)
# =========================
@pytest_asyncio.fixture
async def test_comments(db, auth_user, test_posts):
    post1, post2, post3 = test_posts

    comments = [
        Comment(content="Comment 1", user_id=auth_user.id, post_id=post1.id),
        Comment(content="Comment 2", user_id=auth_user.id, post_id=post1.id),
        Comment(content="Comment 3", user_id=auth_user.id, post_id=post2.id),
        Comment(content="Comment 4", user_id=auth_user.id, post_id=post3.id),
        Comment(content="Comment 5", user_id=auth_user.id, post_id=post3.id),
    ]

    db.add_all(comments)
    await db.commit()

    for c in comments:
        await db.refresh(c)

    return tuple(comments)
