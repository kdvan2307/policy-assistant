from datetime import datetime
from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    message_id: int
    is_helpful: bool


class FeedbackResponse(BaseModel):
    message_id: int
    is_helpful: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackStatsResponse(BaseModel):
    total: int
    helpful_count: int
    not_helpful_count: int
    helpful_rate: float  # phần trăm, vd: 82.5