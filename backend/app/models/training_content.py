import enum
from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ContentType(str, enum.Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"


class TrainingContent(Base):
    __tablename__ = "training_contents"

    __table_args__ = (
        UniqueConstraint(
            "module_id",
            "position",
            name="uq_training_content_module_position",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    module_id: Mapped[int] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )

    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType, name="contenttype"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    text_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    video_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    module = relationship(
        "Module",
        back_populates="training_contents",
    )