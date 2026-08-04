from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Câu hỏi của người dùng")
    session_id: int | None = Field(
        None, description="ID cuộc trò chuyện — để trống nếu bắt đầu cuộc trò chuyện mới"
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    session_id: int  # trả về để client dùng cho lượt hỏi tiếp theo trong cùng session


class ChatMessageResponse(BaseModel):
    id: int          # THÊM DÒNG NÀY
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