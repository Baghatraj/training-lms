from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.module import Module
from app.models.training_content import TrainingContent
from app.models.user import User, UserRole
from app.schemas.training_content import (
    TrainingContentCreate,
    TrainingContentResponse,
    TrainingContentUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Training Content"],
)

@router.post(
    "/modules/{module_id}/contents",
    response_model=TrainingContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_content(
    module_id: int,
    content_data: TrainingContentCreate,
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

    content = TrainingContent(
        module_id=module_id,
        content_type=content_data.content_type,
        title=content_data.title,
        text_content=content_data.text_content,
        video_url=(
            str(content_data.video_url)
            if content_data.video_url
            else None
        ),
        position=content_data.position,
    )

    db.add(content)

    try:
        db.commit()
        db.refresh(content)
    except Exception:
        db.rollback()
        raise

    return content

@router.get(
    "/modules/{module_id}/contents",
    response_model=list[TrainingContentResponse],
)
def list_training_content(
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

    return (
        db.query(TrainingContent)
        .filter(TrainingContent.module_id == module_id)
        .order_by(TrainingContent.position)
        .all()
    )

@router.get(
    "/contents/{content_id}",
    response_model=TrainingContentResponse,
)
def get_training_content(
    content_id: int,
    db: Session = Depends(get_db),
):
    content = (
        db.query(TrainingContent)
        .filter(TrainingContent.id == content_id)
        .first()
    )

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training content not found",
        )

    return content


@router.put(
    "/contents/{content_id}",
    response_model=TrainingContentResponse,
)
def update_training_content(
    content_id: int,
    content_data: TrainingContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.INSTRUCTOR,
        )
    ),
):
    content = (
        db.query(TrainingContent)
        .filter(TrainingContent.id == content_id)
        .first()
    )

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training content not found",
        )

    update_data = content_data.model_dump(
        exclude_unset=True
    )

    if "video_url" in update_data:
        update_data["video_url"] = (
            str(update_data["video_url"])
            if update_data["video_url"] is not None
            else None
        )

    for field, value in update_data.items():
        setattr(content, field, value)

    db.commit()
    db.refresh(content)

    return content

@router.delete(
    "/contents/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_training_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.INSTRUCTOR,
        )
    ),
):
    content = (
        db.query(TrainingContent)
        .filter(TrainingContent.id == content_id)
        .first()
    )

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training content not found",
        )

    db.delete(content)
    db.commit()