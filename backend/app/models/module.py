from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
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

    course = relationship(
        "Course",
        back_populates="modules",
    )

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "position",
            name="uq_module_course_position",
        ),
    )

    training_contents = relationship(
        "TrainingContent",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="TrainingContent.position",
    )

    quiz = relationship(
        "Quiz", back_populates="module", uselist=False, cascade="all, delete-orphan"
    )

    progress = relationship(
        "ModuleProgress",
        back_populates="module",
        cascade="all, delete-orphan",
    )
