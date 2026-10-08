from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    title: Mapped[str]
    body: Mapped[str]

    def __str__(self) -> str:
        return self.title
