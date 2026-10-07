from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(75), unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return self.email
