from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from typing import Optional
from datetime import datetime

from app.Models.expense_type.expense_type import ExpenseType
from app.database.base import Base


class BudgetList(Base):
    __tablename__ = "budget_list"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    name: Mapped[str] = mapped_column(String(200))
    value: Mapped[float] = mapped_column(Float)
    currency: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expense_types.id"), nullable=True)

    type: Mapped[Optional["ExpenseType"]] = relationship()
