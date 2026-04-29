from fastapi import FastAPI
from src.routes import auth, users, posts, comments # Shto comments këtu
from core.db_connection.database import engine, Base

# Kjo rresht krijon tabelat automatikisht sa herë ndizet serveri
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api") # Ndryshoje këtë nga posts në comments

@app.get("/")
def health_check():
    return {"status": "Backend is running", "test_endpoint": "/api/auth/register"}