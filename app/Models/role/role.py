from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Integer
from typing import Optional, List

from app.database.base import Base


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Integer, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(Text, nullable=False)