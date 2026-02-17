from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CurrencyAlchemy(Base):
    __tablename__ = "currency"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float]
    short_name: Mapped[str] = mapped_column(String(3))