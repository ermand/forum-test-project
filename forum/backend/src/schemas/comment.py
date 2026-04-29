from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str
    post_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime


class CommentUpdate(BaseModel):
    content: str

    class Config:
        from_attributes = True
