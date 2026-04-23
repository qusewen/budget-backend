from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from typing import Optional

from app.Models.base_model_type.base_model_type import BaseType


class ExpenseType(BaseType):
    __tablename__ = "expense_types"

    id: Mapped[int] = mapped_column(ForeignKey("base_types.id"), primary_key=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "expense"
    }