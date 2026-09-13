from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourseAssignment(Base):
    __tablename__ = "course_assignments"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_course_assignment_user_course",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="course_assignments",
    )

    course = relationship(
        "Course",
        back_populates="assignments",
    )