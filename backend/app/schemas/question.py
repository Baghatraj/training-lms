from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AnswerCreate(BaseModel):
    answer_text: str = Field(min_length=1, max_length=500)
    position: int = Field(ge=1)
    is_correct: bool


class QuestionCreate(BaseModel):
    question_text: str = Field(min_length=1, max_length=1000)
    position: int = Field(ge=1)
    answers: list[AnswerCreate] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_answers(self):
        correct_answers = [
            answer for answer in self.answers
            if answer.is_correct
        ]

        if len(correct_answers) != 1:
            raise ValueError(
                "A question must have exactly one correct answer."
            )

        positions = [answer.position for answer in self.answers]

        if len(positions) != len(set(positions)):
            raise ValueError(
                "Answer positions must be unique."
            )

        return self

class QuestionUpdate(BaseModel):
    question_text: str = Field(min_length=1, max_length=1000)
    position: int = Field(ge=1)
    answers: list[AnswerCreate] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_answers(self):
        correct_answers = [
            answer for answer in self.answers
            if answer.is_correct
        ]

        if len(correct_answers) != 1:
            raise ValueError(
                "A question must have exactly one correct answer."
            )

        positions = [answer.position for answer in self.answers]

        if len(positions) != len(set(positions)):
            raise ValueError(
                "Answer positions must be unique."
            )

        return self


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: str
    position: int
    is_correct: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    position: int
    created_at: datetime
    updated_at: datetime
    answers: list[AnswerResponse]

    model_config = ConfigDict(from_attributes=True)

class LearnerAnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: str
    position: int

    model_config = ConfigDict(from_attributes=True)


class LearnerQuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    position: int
    answers: list[LearnerAnswerResponse]

    model_config = ConfigDict(from_attributes=True)