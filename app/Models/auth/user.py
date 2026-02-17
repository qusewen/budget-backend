from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Models.role.role import Role
from app.database.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column( primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int]
    isactive: Mapped[bool] = mapped_column(default=False)
    password: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[int] = mapped_column(ForeignKey('role.id'), nullable=False)

    role: Mapped["Role"] = relationship()
