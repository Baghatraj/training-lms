from app.auth.dependencies import UserRole, require_roles
from app.database import get_db
from app.models.answer import Answer
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/quizzes",
    tags=["Questions"],
)


@router.post(
    "/{quiz_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    quiz_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INSTRUCTOR)),
):
    quiz = db.scalar(select(Quiz).where(Quiz.id == quiz_id))

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    existing_question = db.scalar(
        select(Question).where(
            Question.quiz_id == quiz_id,
            Question.position == question_data.position,
        )
    )

    if existing_question is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A question with this position already exists in this quiz.",
        )

    question = Question(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        position=question_data.position,
    )

    db.add(question)
    db.flush()

    for answer_data in question_data.answers:
        answer = Answer(
            question_id=question.id,
            answer_text=answer_data.answer_text,
            position=answer_data.position,
            is_correct=answer_data.is_correct,
        )

        db.add(answer)

    db.commit()
    db.refresh(question)

    return question


@router.put(
    "/{quiz_id}/questions/{question_id}",
    response_model=QuestionResponse,
)
def update_question(
    quiz_id: int,
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INSTRUCTOR)),
):

    question = db.scalar(
        select(Question).where(
            Question.id == question_id,
            Question.quiz_id == quiz_id,
        )
    )

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    existing_question = db.scalar(
        select(Question).where(
            Question.quiz_id == quiz_id,
            Question.position == question_data.position,
            Question.id != question_id,
        )
    )

    if existing_question is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A question with this position already exists in this quiz.",
        )

    question.question_text = question_data.question_text
    question.position = question_data.position

    question.answers.clear()

    for answer_data in question_data.answers:
        answer = Answer(
            answer_text=answer_data.answer_text,
            position=answer_data.position,
            is_correct=answer_data.is_correct,
        )

        question.answers.append(answer)

    db.commit()
    db.refresh(question)

    return question

@router.delete(
    "/{quiz_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_question(
    quiz_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN,UserRole.INSTRUCTOR)),
):

    question = db.scalar(
        select(Question).where(
            Question.id == question_id,
            Question.quiz_id == quiz_id,
        )
    )

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    db.delete(question)
    db.commit()