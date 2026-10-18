from collections.abc import Sequence
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select, func

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
        query = select(Post).where(Post.status == PostStatus.PUBLISHED).order_by(Post.id)
        posts = await self.session.scalars(query)
        return posts.all()

    async def list_by_authors(self, author_ids: list[int]) -> Sequence[Post]:
        query = (
            select(Post)
            .where(
                Post.author_id.in_(author_ids),
                Post.status == PostStatus.PUBLISHED,
            )
            .order_by(Post.created_at.desc())
        )
        posts = await self.session.scalars(query)
        return posts.all()

    async def list_by_author(
        self, author_id: int, status: PostStatus | None = None
    ) -> Sequence[Post]:
        query = (
            select(Post)
            .where(Post.author_id == author_id)
            .order_by(Post.created_at.desc())
        )
        if status is not None:
            query = query.where(Post.status == status)
        posts = await self.session.scalars(query)
        return posts.all()

    async def list_by_ids(self, post_ids: list[int]) -> Sequence[Post]:
        query = (
            select(Post)
            .where(Post.id.in_(post_ids))
            .order_by(Post.created_at.desc())
        )
        posts = await self.session.scalars(query)
        return posts.all()

    async def count_by_authors(self, author_ids: list[int]) -> dict[int, int]:
        query = (
            select(Post.author_id, func.count())
            .where(
                Post.author_id.in_(author_ids),
                Post.status == PostStatus.PUBLISHED,
            )
            .group_by(Post.author_id)
        )
        result = await self.session.execute(query)
        return dict(result.all())

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

    async def list_by_posts(self, post_ids: list[int]) -> Sequence[Comment]:
        query = (
            select(Comment)
            .where(Comment.post_id.in_(post_ids))
            .order_by(Comment.created_at.desc())
        )
        comments = await self.session.scalars(query)
        return comments.all()

    async def count_by_posts(self, post_ids: list[int]) -> dict[int, int]:
        query = (
            select(Comment.post_id, func.count())
            .where(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
        )
        result = await self.session.execute(query)
        return dict(result.all())

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
