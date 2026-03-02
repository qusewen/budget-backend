from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.database.base import Base

class BaseType(Base):
    __tablename__ = "base_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "base"
    }