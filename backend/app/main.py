from app import database
from app.routers.auth import router as auth_router
from app.routers.courses import router as courses_router
from app.routers.modules import router as modules_router
from app.routers.questions import router as questions_router
from app.routers.quizzes import router as quizzes_router
from app.routers.training_contents import router as training_contents_router
from app.routers.course_assignments import router as course_assignments_router
from fastapi import FastAPI

app = FastAPI(title="Training LMS API")
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(modules_router)
app.include_router(training_contents_router)
app.include_router(quizzes_router)
app.include_router(questions_router)
app.include_router(course_assignments_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}