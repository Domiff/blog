from collections.abc import Sequence
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.blog.enums import PostStatus
from backend.blog.models import Post
from backend.core.database import BaseRepository


class PostRepository(BaseRepository):
    async def create(self, data: dict[str, Any]) -> Post:
        post = Post(**data)
        self.session.add(post)
        await self.session.flush()
        return post

    async def list(self) -> Sequence[Post]:
        query = select(Post).order_by(Post.id)
        posts = await self.session.scalars(query)
        return posts.all()

    async def get_by_id(self, id: int) -> Post | None:
        return await self.session.get(Post, id)

    async def update(self, post: Post, data: dict[str, Any]) -> Post:
        for key, value in data.items():
            if not hasattr(Post, key):
                raise AttributeError(f"Post has no field {key!r}")
            if value is None:
                continue
            setattr(post, key, value)
        await self.session.flush()
        return post

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)
        await self.session.flush()

    async def publish(self, post: Post) -> Post:
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.now(tz=UTC)
        await self.session.flush()
        return post
