from collections.abc import Sequence
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.blog.enums import PostStatus
from backend.blog.models import Post, Comment
from backend.core.database import BaseRepository


class PostRepository(BaseRepository):
    async def create(self, data: dict[str, Any]) -> Post:
        post = Post(**data)
        self.session.add(post)
        await self.session.flush()
        return post

    async def list(self) -> Sequence[Post]:
        query = select(Post).order_by(Post.id).options(joinedload(Post.author))
        posts = await self.session.scalars(query)
        return posts.all()

    async def list_by_author(self, author_id: int) -> Sequence[Post]:
        query = select(Post).options(joinedload(Post.author)).where(Post.author_id == author_id)
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


class CommentRepository(BaseRepository):
    async def create(self, data: dict[str, Any]) -> Comment:
        comment = Comment(**data)
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def list_by_post(self, post_id: int) -> Sequence[Comment]:
        query = select(Comment).where(Comment.post_id == post_id)
        comment = await self.session.scalars(query)
        return comment.all()

    async def get_by_id(self, id: int) -> Comment | None:
        return await self.session.get(Comment, id)

    async def update(self, comment: Comment, data: dict[str, Any]) -> Comment:
        for key, value in data.items():
            if not hasattr(Comment, key):
                raise AttributeError(f"Comment has no field {key!r}")
            if value is None:
                continue
            setattr(comment, key, value)
        await self.session.flush()
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.session.delete(comment)
        await self.session.flush()
