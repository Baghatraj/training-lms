from app import database
from fastapi import FastAPI

app = FastAPI(title="Training LMS API")


@app.get("/health")
def health_check():
    return {"status": "ok"}