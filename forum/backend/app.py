from fastapi import FastAPI
from core.db_connection.database import engine, Base
from src.models import user, posts, comments

# Këtu krijohet variabli 'app' që i mungonte Python-it
app = FastAPI()

# Kjo komandë krijon tabelat në forum.db
Base.metadata.create_all(bind=engine)

@app.get("/")
def check_health():
    return {"status": "Gati!", "db": "E lidhur"}