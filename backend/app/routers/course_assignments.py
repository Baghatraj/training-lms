from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.course import Course
from app.models.course_assignment import CourseAssignment
from app.models.user import User, UserRole
from app.schemas.course_assignment import CourseAssignmentResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/courses",
    tags=["Course Assignments"],
)


@router.post(
    "/{course_id}/assignments/{user_id}",
    response_model=CourseAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_course(
    course_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INSTRUCTOR)),
):
    course = db.scalar(select(Course).where(Course.id == course_id))

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    existing_assignment = db.scalar(
        select(CourseAssignment).where(
            CourseAssignment.course_id == course_id,
            CourseAssignment.user_id == user_id,
        )
    )

    if existing_assignment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course is already assigned to this user.",
        )

    assignment = CourseAssignment(
        course_id=course_id,
        user_id=user_id,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment
