from pydantic import BaseModel
from typing import List, Generic, TypeVar

T = TypeVar('T')

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


    class Config:
        from_attributes = True