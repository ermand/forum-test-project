from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
