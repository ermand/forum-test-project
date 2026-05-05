from math import ceil
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, computed_field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T | None = None
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    details: dict[str, Any] | list[Any] | None = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @computed_field
    @property
    def limit(self) -> int:
        return self.page_size


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int = Field(ge=0)

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 0
        return ceil(self.total_items / self.page_size)

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @computed_field
    @property
    def has_previous(self) -> bool:
        return self.page > 1


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PaginationMeta

    model_config = ConfigDict(from_attributes=True)
