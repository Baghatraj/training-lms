from datetime import datetime

from app.schemas.question import LearnerQuestionResponse
from pydantic import BaseModel, ConfigDict, Field


class QuizCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    passing_score: int = Field(ge=0, le=100)


class QuizResponse(BaseModel):
    id: int
    module_id: int
    title: str
    passing_score: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearnerQuizResponse(BaseModel):
    id: int
    module_id: int
    title: str
    passing_score: int
    questions: list[LearnerQuestionResponse]

    model_config = ConfigDict(from_attributes=True)