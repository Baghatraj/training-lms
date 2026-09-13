from datetime import datetime

from app.models.training_content import ContentType
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class TrainingContentCreate(BaseModel):
    content_type: ContentType
    title: str = Field(min_length=1, max_length=200)
    text_content: str | None = None
    video_url: HttpUrl | None = None
    position: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_content(self):
        if self.content_type == ContentType.TEXT:
            if not self.text_content or not self.text_content.strip():
                raise ValueError(
                    "text_content is required for TEXT content"
                )

            if self.video_url is not None:
                raise ValueError(
                    "video_url must not be provided for TEXT content"
                )

        elif self.content_type == ContentType.VIDEO:
            if self.video_url is None:
                raise ValueError(
                    "video_url is required for VIDEO content"
                )

            if self.text_content is not None:
                raise ValueError(
                    "text_content must not be provided for VIDEO content"
                )

        return self


class TrainingContentUpdate(BaseModel):
    content_type: ContentType | None = None
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    text_content: str | None = None
    video_url: HttpUrl | None = None
    position: int | None = Field(
        default=None,
        ge=1,
    )


class TrainingContentResponse(BaseModel):
    id: int
    module_id: int
    content_type: ContentType
    title: str
    text_content: str | None
    video_url: str | None
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)