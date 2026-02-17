from typing import Optional


from pydantic import BaseModel, Field
from datetime import datetime

class BudgetType(BaseModel):
    id: int
    name: str
    description: str
    content: Optional[str] = None

    class Config:
        from_attributes = True

class BudgetList(BaseModel):
    date: datetime = Field(...)
    name: str = Field(...)
    value: float = Field(...)
    currency: int = Field(...)
    description: str = Field(...)
    content: Optional[str] = Field(None)
    type: BudgetType

    class Config:
        from_attributes = True

class BudgetListResponse(BudgetList):
    id: int = Field(...)
