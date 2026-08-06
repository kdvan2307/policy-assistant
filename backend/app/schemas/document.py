from datetime import datetime
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    title: str
    file_type: str
    allowed_roles: list[str]
    chunks_created: int


class DocumentListResponse(BaseModel):
    id: int
    title: str
    file_type: str
    allowed_roles: list[str]
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True