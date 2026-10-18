from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.blog.models import Post
    from backend.profile.models import Profile


class PostBookmark(Base):
    __tablename__ = "post_bookmarks"
    __table_args__ = (
        UniqueConstraint("owner_id", "post_id", name="uq_post_bookmarks_owner_id_post_id"),
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))

    post: Mapped["Post"] = relationship(back_populates="bookmarks", lazy="raise", passive_deletes=True)
    owner: Mapped["Profile"] = relationship(back_populates="bookmarks", lazy="raise", passive_deletes=True)

    def __str__(self) -> str:
        return f"Post bookmark {self.id}"
