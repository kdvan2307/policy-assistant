from datetime import datetime
from pydantic import BaseModel


class RequestLogResponse(BaseModel):
    id: int
    method: str
    endpoint: str
    status_code: int
    duration_ms: float
    error_message: str | None
    user_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True