from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GuestLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nickname: str


class UserResponse(BaseModel):
    id: int
    nickname: str
    auth_type: str
    created_at: datetime

    class Config:
        from_attributes = True
