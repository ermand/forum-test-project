from fastapi import FastAPI
from src.routes import auth, users , posts
import src.models
app = FastAPI()


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "Backend is running", "test_endpoint": "/api/auth/register"}