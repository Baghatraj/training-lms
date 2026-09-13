from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.course import Course
from app.models.module import Module
from app.models.user import User, UserRole
from app.schemas.module import (
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/courses",
    tags=["Modules"],
)


@router.post(
    "/{course_id}/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_module(
    course_id: int,
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.INSTRUCTOR,
        )
    ),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    module = Module(
        course_id=course_id,
        title=module_data.title,
        description=module_data.description,
        position=module_data.position,
    )

    db.add(module)
    try:
        db.commit()
        db.refresh(module)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A module with this position already exists in this course.",
        )

    return module


@router.get(
    "/{course_id}/modules",
    response_model=list[ModuleResponse],
)
def list_modules(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return (
        db.query(Module)
        .filter(Module.course_id == course_id)
        .order_by(Module.position)
        .all()
    )

@router.get(
    "/modules/{module_id}",
    response_model=ModuleResponse,
)
def get_module(
    module_id: int,
    db: Session = Depends(get_db),
):
    module = (
        db.query(Module)
        .filter(Module.id == module_id)
        .first()
    )

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    return module

@router.put(
    "/modules/{module_id}",
    response_model=ModuleResponse,
)
def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.INSTRUCTOR,
        )
    ),
):
    module = (
        db.query(Module)
        .filter(Module.id == module_id)
        .first()
    )

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    update_data = module_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(module, field, value)

    db.commit()
    db.refresh(module)

    return module

@router.put(
    "/modules/{module_id}",
    response_model=ModuleResponse,
)
def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.INSTRUCTOR,
        )
    ),
):
    module = (
        db.query(Module)
        .filter(Module.id == module_id)
        .first()
    )

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    update_data = module_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(module, field, value)

    db.commit()
    db.refresh(module)

    return module