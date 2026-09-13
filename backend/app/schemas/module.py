from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ModuleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    position: int = Field(ge=1)


class ModuleUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    position: int | None = Field(
        default=None,
        ge=1,
    )


class ModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)