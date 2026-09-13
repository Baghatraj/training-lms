from datetime import datetime, timezone

from app.database import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ModuleProgress(Base):
    __tablename__ = "module_progress"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "module_id",
            name="uq_module_progress_user_module",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    module_id: Mapped[int] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="module_progress",
    )

    module = relationship(
        "Module",
        back_populates="progress",
    )