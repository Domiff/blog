from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


if TYPE_CHECKING:
    from backend.profile.models import Profile


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(75), unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    profile: Mapped["Profile"] = relationship(back_populates="user", lazy="raise")

    def __repr__(self) -> str:
        return self.email
