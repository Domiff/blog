from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.blog.enums import PostStatus
from backend.core.database import Base


if TYPE_CHECKING:
    from backend.profile.models import Profile


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
    author_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    author: Mapped["Profile"] = relationship(back_populates="posts", lazy="raise")

    def __str__(self) -> str:
        return self.title
