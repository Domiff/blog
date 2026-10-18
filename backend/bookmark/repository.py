from typing import Sequence

from sqlalchemy import select

from backend.core.database import BaseRepository
from backend.bookmark.models import PostBookmark
from backend.blog.models import Post
from backend.blog.enums import PostStatus

class PostBookmarkRepository(BaseRepository):
    async def create(self, data: dict) -> PostBookmark:
        bookmark = PostBookmark(**data)
        self.session.add(bookmark)
        await self.session.flush()
        return bookmark

    async def list(self) -> Sequence[PostBookmark]:
        query = select(PostBookmark).order_by(PostBookmark.created_at.desc())
        bookmarks = await self.session.scalars(query)
        return bookmarks.all()

    async def list_by_owner(self, owner_id: int) -> Sequence[PostBookmark]:
        query = select(PostBookmark).join(PostBookmark.post).where(PostBookmark.owner_id == owner_id, Post.status == PostStatus.PUBLISHED).order_by(PostBookmark.created_at.desc())
        bookmarks = await self.session.scalars(query)
        return bookmarks.all()

    async def get_by_id(self, id: int) -> PostBookmark | None:
        return await self.session.get(PostBookmark, id)

    async def get_by_owner_and_post(self, owner_id: int, post_id: int) -> PostBookmark | None:
        query = select(PostBookmark).where(
            PostBookmark.owner_id == owner_id,
            PostBookmark.post_id == post_id,
        )
        return await self.session.scalar(query)

    async def delete(self, bookmark: PostBookmark) -> None:
        await self.session.delete(bookmark)
        await self.session.flush()
