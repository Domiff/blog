from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


if TYPE_CHECKING:
    from backend.auth.models import User
    from backend.blog.models import Post


class Profile(Base):
    __tablename__ = "profiles"

    username: Mapped[str] = mapped_column(String(32), unique=True)
    bio: Mapped[str | None] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="profile", lazy="raise")
    posts: Mapped["Post"] = relationship(back_populates="profile", lazy="raise")

    def __str__(self) -> str:
        return self.username
