from app import database
from app.routers.auth import router as auth_router
from app.routers.courses import router as courses_router
from fastapi import FastAPI

app = FastAPI(title="Training LMS API")
app.include_router(auth_router)
app.include_router(courses_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}