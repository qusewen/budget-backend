from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, ForeignKey
from typing import Optional

from app.Models.base_model_type.base_model_type import BaseType


class IncomeType(BaseType):
    __tablename__ = "income_types"

    id: Mapped[int] = mapped_column(ForeignKey("base_types.id"), primary_key=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "income"
    }