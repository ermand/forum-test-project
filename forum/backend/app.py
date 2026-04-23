import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Forum Project API")

@app.get("/")
def home():
    return {"message": "API is working and Database is connected! 🚀"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)