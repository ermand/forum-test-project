import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from src.schemas.posts import PostResponse
from src.utils import PaginatedResponse


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

    @field_validator("username", "email", mode="before")
    @classmethod
    def normalize_identity(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<> ]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    user_info: UserResponse
    posts: PaginatedResponse[PostResponse]

    model_config = ConfigDict(from_attributes=True)
