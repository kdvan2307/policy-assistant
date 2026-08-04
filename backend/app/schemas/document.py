from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    title: str
    file_type: str
    allowed_roles: list[str]
    chunks_created: int