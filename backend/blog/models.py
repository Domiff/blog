from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from backend.blog.enums import PostStatus
from backend.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(255), index=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status", values_callable=lambda e: [m.value for m in e]),
        default=PostStatus.DRAFT,
        server_default=PostStatus.DRAFT.value,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    def __str__(self) -> str:
        return self.title
