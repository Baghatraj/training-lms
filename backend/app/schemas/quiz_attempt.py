from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuizAnswerSubmission(BaseModel):
    question_id: int
    selected_answer_id: int


class QuizAttemptCreate(BaseModel):
    answers: list[QuizAnswerSubmission] = Field(min_length=1)


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    score: int
    passed: bool
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)