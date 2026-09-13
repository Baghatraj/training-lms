from app.database import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class QuizAttemptAnswer(Base):
    __tablename__ = "quiz_attempt_answers"

    id: Mapped[int] = mapped_column(primary_key=True)

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    selected_answer_id: Mapped[int] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
    )

    attempt = relationship(
        "QuizAttempt",
        back_populates="answers",
    )

    question = relationship(
        "Question",
        back_populates="attempt_answers",
    )

    selected_answer = relationship(
        "Answer",
        back_populates="attempt_answers",
    )

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_attempt_question",
        ),
    )
