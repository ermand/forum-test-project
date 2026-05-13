from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):

    content: str = Field(..., min_length=1, max_length=1000)
    post_id: UUID


class CommentResponse(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    post_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)