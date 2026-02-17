from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.Models.currency.currency_model import CurrencyResponse


class WalletBase(BaseModel):
    value: float = Field(..., ge=0, description="Сумма/баланс кошелька")
    user_id: int = Field(..., description="ID пользователя-владельца")
    description: Optional[str] = Field(None, max_length=255, description="Описание кошелька")
    currency_id: int = Field(..., description="ID валюты")
    is_general: bool = Field(False, description="Является ли основным кошельком")


class WalletCreate(WalletBase):
    pass


class WalletUpdate(BaseModel):
    value: Optional[float] = Field(None, ge=0, description="Сумма/баланс кошелька")
    description: Optional[str] = Field(None, max_length=255, description="Описание кошелька")
    currency_id: Optional[int] = Field(None, description="ID валюты")
    is_general: Optional[bool] = Field(None, description="Является ли основным кошельком")


class WalletResponse(WalletBase):
    id: int
    currency: CurrencyResponse

    class Config:
        from_attributes = True