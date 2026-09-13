from app.auth.dependencies import UserRole, require_roles
from app.database import get_db
from app.models.course_assignment import CourseAssignment
from app.models.module import Module
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.quiz import LearnerQuizResponse, QuizCreate, QuizResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

router = APIRouter(
    prefix="/modules",
    tags=["Quizzes"],
)


@router.post(
    "/{module_id}/quiz",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quiz(
    module_id: int,
    quiz_data: QuizCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.INSTRUCTOR,
        )
    ),
    db: Session = Depends(get_db),
):
    module = db.scalar(select(Module).where(Module.id == module_id))

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found.",
        )

    existing_quiz = db.scalar(select(Quiz).where(Quiz.module_id == module_id))

    if existing_quiz is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A quiz already exists for this module.",
        )

    quiz = Quiz(
        module_id=module_id,
        title=quiz_data.title,
        passing_score=quiz_data.passing_score,
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


@router.get(
    "/{module_id}/quiz",
    response_model=QuizResponse,
)
def get_quiz(
    module_id: int,
    db: Session = Depends(get_db),
):
    quiz = db.scalar(select(Quiz).where(Quiz.module_id == module_id))

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    return quiz

@router.get(
    "/{module_id}/quiz/questions",
    response_model=LearnerQuizResponse,
)
def get_learner_quiz(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    module = db.get(Module, module_id)

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found.",
        )

    assignment = db.scalar(
        select(CourseAssignment).where(
            CourseAssignment.user_id == current_user.id,
            CourseAssignment.course_id == module.course_id,
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this course.",
        )

    quiz = db.scalar(
        select(Quiz)
        .where(Quiz.module_id == module_id)
        .options(
            selectinload(Quiz.questions)
            .selectinload(Question.answers)
        )
    )

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    return quiz