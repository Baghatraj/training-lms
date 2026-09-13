from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModuleProgressResponse(BaseModel):
    id: int
    user_id: int
    module_id: int
    completed: bool
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)