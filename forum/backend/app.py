from fastapi import FastAPI

from core.db_connection.database import engine, Base
from src.routes import auth, users, posts, comments

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "Backend is running", "test_endpoint": "/api/auth/register"}
