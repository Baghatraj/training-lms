from datetime import datetime, timezone

from app.auth.dependencies import UserRole, require_roles
from app.database import get_db
from app.models.answer import Answer
from app.models.course_assignment import CourseAssignment
from app.models.module_progress import ModuleProgress
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_attempt_answer import QuizAttemptAnswer
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate
from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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

@router.post(
    "/{quiz_id}/attempts",
    response_model=QuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_quiz(
    quiz_id: int,
    data: QuizAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    quiz = db.scalar(
        select(Quiz)
        .where(Quiz.id == quiz_id)
        .options(
            selectinload(Quiz.module),
            selectinload(Quiz.questions)
            .selectinload(Question.answers),
        )
    )

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    assignment = db.scalar(
        select(CourseAssignment).where(
            CourseAssignment.user_id == current_user.id,
            CourseAssignment.course_id == quiz.module.course_id,
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this course.",
        )

    questions = {
        question.id: question
        for question in quiz.questions
    }

    if len(data.answers) != len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must answer every question.",
        )

    submitted_question_ids = {
        answer.question_id
        for answer in data.answers
    }

    if len(submitted_question_ids) != len(data.answers):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A question can only be answered once.",
        )

    if submitted_question_ids != set(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submitted questions do not match the quiz questions.",
        )

    score_count = 0

    attempt_answers = []

    for submitted_answer in data.answers:
        question = questions[submitted_answer.question_id]

        selected_answer = next(
            (
                answer
                for answer in question.answers
                if answer.id == submitted_answer.selected_answer_id
            ),
            None,
        )

        if selected_answer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected answer does not belong to the question.",
            )

        if selected_answer.is_correct:
            score_count += 1

        attempt_answers.append(
            QuizAttemptAnswer(
                question_id=question.id,
                selected_answer_id=selected_answer.id,
            )
        )

    score = round(
        score_count / len(questions) * 100
    )

    passed = score >= quiz.passing_score

    if passed:
        progress = db.scalar(
            select(ModuleProgress).where(
                ModuleProgress.user_id == current_user.id,
                ModuleProgress.module_id == quiz.module_id,
            )
        )

    if progress is None:
        progress = ModuleProgress(
            user_id=current_user.id,
            module_id=quiz.module_id,
            completed=True,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(progress)
    else:
        progress.completed = True
        progress.completed_at = datetime.now(timezone.utc)

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=score,
        passed=passed,
    )

    db.add(attempt)
    db.flush()

    for attempt_answer in attempt_answers:
        attempt_answer.attempt_id = attempt.id
        db.add(attempt_answer)

    db.commit()
    db.refresh(attempt)

    return attempt