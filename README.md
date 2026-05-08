# 🏛️ Forum API Project

A modern, asynchronous REST API for a forum platform built with **FastAPI**.  
This project supports **user authentication**, **post management**, and a **commenting system**.

---

# 🚀 Tech Stack

- **FastAPI** — High-performance web framework for building APIs.
- **SQLAlchemy 2.0** — Advanced SQL toolkit and asynchronous ORM.
- **Aiosqlite** — Async SQLite driver for testing and local development.
- **Pydantic V2** — Data validation and settings management using type annotations.
- **Pytest & Pytest-asyncio** — Testing framework for asynchronous applications.
- **UV** — Extremely fast Python package installer and resolver.

---

# 📂 Project Structure

```bash
forum-test-project/
│
├── forum/
│   └── backend/
│       ├── core/
│       ├── src/
│       │   ├── models/
│       │   ├── routes/
│       │   ├── schemas/
│       │   ├── services/
│       │   └── tests/
│       ├── alembic/
│       ├── app.py
│       ├── pyproject.toml
│       └── .env
```

---

# 🛠️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/ermand/forum-test-project.git
cd forum-test-project/forum/backend
```

---

## 2️⃣ Create Virtual Environment

```bash
uv venv
```

---

## 3️⃣ Install Dependencies

```bash
uv sync
```

---

# ⚙️ Environment Configuration

Create a `.env` file inside the `backend` directory:

```env
DATABASE_URL=sqlite:///./forum.db
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# ▶️ Running the Application

```bash
cd forum
cd backend

uv run uvicorn app:app --reload
```

---

# 🌐 API Endpoints

| Service | URL |
|---|---|
| API Base URL | `http://127.0.0.1:8000` |
| Swagger Docs | `http://127.0.0.1:8000/docs` |

---

# 🧪 Running Tests

The project includes comprehensive tests for:

- Authentication
- Posts
- Comments
- Services
- Routes

Testing uses an **in-memory SQLite database** to keep tests fast and isolated.

## Run All Tests

```bash
uv run pytest tests
```

# 🔐 Features

✅ JWT Authentication  
✅ Async SQLAlchemy ORM  
✅ CRUD Operations for Posts  
✅ Commenting System  
✅ Route & Service Layer Testing  
✅ Environment-Based Configuration  
✅ Alembic Database Migrations  
✅ Pagination Support  
✅ Rate Limiting Middleware  

---
# 🧱 Built With

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- Pydantic V2
- PyJWT
- Alembic
- Pytest

---

# 👨‍💻 Author

Developed by **Gledis Selfaj**.

---
