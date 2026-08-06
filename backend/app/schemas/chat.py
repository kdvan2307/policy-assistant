from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    session_id: int
    message_id: int  # THÊM MỚI — cần để gọi POST /chat/feedback ở Bước 21


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: list[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True