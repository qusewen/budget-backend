from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BudgetTypeResponse(BaseModel):
    id: int
    name: str
    description: str
    content: Optional[str] = None

    class Config:
        from_attributes = True

class BudgetListCreate(BaseModel):
    date: datetime = Field(...)
    name: str = Field(...)
    value: float = Field(...)
    currency: int = Field(...)
    description: str = Field(...)
    content: Optional[str] = Field(None)
    type_id: int = Field(...)

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