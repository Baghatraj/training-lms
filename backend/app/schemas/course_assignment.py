from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseAssignmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)