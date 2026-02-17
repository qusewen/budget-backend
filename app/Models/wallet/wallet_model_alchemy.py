from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.Models.currency.currency_alchemy import CurrencyAlchemy

from app.database.base import Base


class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=False)
    is_general: Mapped[bool]

    currency: Mapped[Optional["CurrencyAlchemy"]] = relationship()

