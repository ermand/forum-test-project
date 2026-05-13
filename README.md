# 🏛️ Forum API Project

A modern **asynchronous REST API backend** for a forum platform built with **FastAPI**.

This project provides:
- User authentication (JWT RS256)
- Post management
- Comment system
- Async database support (SQLite + PostgreSQL)
- Full test coverage with Pytest

---

# 🚨 Project Scope

This repository contains the **backend only**.

There is currently **no frontend included** in this project.

All functionality is exposed through a REST API.

---

# 🚀 Tech Stack

- FastAPI — High-performance async API framework  
- SQLAlchemy 2.0 — Async ORM  
- Aiosqlite — SQLite async driver  
- PostgreSQL (optional) — Production database support  
- Pydantic v2 — Data validation & settings  
- PyJWT / RSA (RS256) — Secure authentication  
- Alembic — Database migrations  
- Pytest & pytest-asyncio — Testing framework  
- UV — Fast Python package manager  

---

# 📂 Project Structure

forum-test-project/
└── forum/
    └── backend/
        ├── core/
        │   ├── auth/
        │   └── db_connection/
        ├── src/
        │   ├── config/
        │   ├── models/
        │   ├── routes/
        │   ├── schemas/
        │   ├── services/
        │   └── utils/
        ├── tests/
        ├── alembic/
        ├── app.py
        ├── alembic.ini
        ├── forum.db
        ├── test.db
        ├── pyproject.toml
        ├── uv.lock
        ├── .env
        └── .env.example

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

git clone https://github.com/ermand/forum-test-project.git
cd forum-test-project/forum/backend

---

## 2️⃣ Create Virtual Environment

uv venv

---

## 3️⃣ Install Dependencies

uv sync

---

# ⚙️ Environment Configuration

Create a `.env` file in `backend/`:

PROJECT_NAME=forum-test-project 

DEBUG=true

DATABASE_URL=sqlite:///./forum.db

POSTGRES_URL=#

APP_ENV=development

JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=1

JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"

---

# 🔐 Authentication System

This project uses RS256 JWT authentication.

- Private key → signs tokens  
- Public key → verifies tokens  

More secure than HS256 (no shared secret).

---

# ▶️ Running the Application

cd forum

cd backend

uv run uvicorn app:app --reload

---

# 🌐 API Endpoints

Base API: http://127.0.0.1:8000  
Swagger UI: http://127.0.0.1:8000/docs  

---

# 🧪 Running Tests

uv run pytest tests

---

# 🔑 Key Features

- JWT Authentication (RS256)
- Refresh token system
- Async SQLAlchemy ORM
- Posts CRUD system
- Comments system
- Pagination support
- Rate limiting middleware
- Environment-based configuration
- Alembic migrations
- Full test suite

---

# 🗄️ Database Support

SQLite (default):
DATABASE_URL=sqlite:///./forum.db

PostgreSQL (optional):
POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/forum_db

---

# 🔑 Generate RSA Keys

openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

---

# 👨‍💻 Author

Developed by Gledis Selfaj
