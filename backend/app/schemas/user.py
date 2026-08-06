from datetime import datetime
from pydantic import BaseModel


class UserListResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateRoleRequest(BaseModel):
    role: str