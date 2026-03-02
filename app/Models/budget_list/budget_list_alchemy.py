from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from typing import Optional
from datetime import datetime

from app.Models.base_model_type.base_model_type import BaseType
from app.database.base import Base


class BudgetList(Base):
    __tablename__ = "budget_list"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    name: Mapped[str] = mapped_column(String(200))
    value: Mapped[float] = mapped_column(Float)
    currency: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    type_budget: Mapped[str] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("base_types.id"), nullable=True)
    currency_value: Mapped[Optional[float]] = mapped_column(Float)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"), nullable=True)

    type: Mapped[Optional["BaseType"]] = relationship()
