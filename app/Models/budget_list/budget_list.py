from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from enum import Enum


class BudgetTypeResponse(BaseModel):
    id: int
    name: str
    description: str
    content: Optional[str] = None

    class Config:
        from_attributes = True


class SortField(str, Enum):
    ID = "id"
    NAME = "name"
    VALUE = "value"
    CONTENT = "content"
    TYPE = "type_id"
    CURRENCY = "currency"
    DATE = "date"

class BudgetListCreate(BaseModel):
    date: datetime = Field(...)
    name: str = Field(...)
    value: float = Field(...)
    currency: int = Field(...)
    description: str = Field(...)
    content: Optional[str] = Field(None)
    type_id: int = Field(...)
    wallet_id: int = Field(...)

    class Config:
        from_attributes = True

class BudgetListUpdate(BaseModel):
        date: Optional[datetime] = None
        name: Optional[str] = None
        value: Optional[float] = None
        currency: Optional[int] = None
        description: Optional[str] = None
        content: Optional[str] = None
        type_id: Optional[int] = None

        class Config:
            from_attributes = True

class BudgetListResponse(BaseModel):
    id: int
    date: datetime
    name: str
    value: float
    currency: int
    description: str
    content: Optional[str] = None
    type: BudgetTypeResponse

    class Config:
        from_attributes = True