from datetime import datetime

from strawberry import type, input, field, mutation, asdict, Schema, Info

from backend.blog.repository import PostRepository
from backend.blog.models import Post
from backend.core.database import get_session


@input
class PostSchemaIn:
    title: str | None
    body: str | None


@type
class PostSchemaOut:
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, post: Post) -> "PostSchemaOut":
        return cls(
            id=post.id,
            title=post.title,
            body=post.body,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )


@type
class Query:
    @field
    async def get_post_list(self, info: Info) -> list[PostSchemaOut] | None:
        repo = PostRepository(info.context.session)
        posts = await repo.list()
        if not posts:
            return None
        return [PostSchemaOut.from_model(post) for post in posts]

    @field
    async def get_post_by_id(self, info: Info, post_id: int) -> PostSchemaOut | None:
        repo = PostRepository(info.context.session)
        post = await repo.get_by_id(post_id)
        if not post:
            return None
        return PostSchemaOut.from_model(post)


@type
class Mutation:
    @mutation
    async def create_post(self, info: Info, post_schema: PostSchemaIn) -> PostSchemaOut:
        repo = PostRepository(info.context.session)
        post = await repo.create(asdict(post_schema))
        return PostSchemaOut.from_model(post)

    @mutation
    async def update_post(
        self, info: Info, post_id: int, post_schema: PostSchemaIn
    ) -> PostSchemaOut | None:
        repo = PostRepository(info.context.session)
        post = await repo.get_by_id(post_id)
        if post:
            post = await repo.update(post, asdict(post_schema))
            return PostSchemaOut.from_model(post)

    @mutation
    async def delete_post(self, info: Info, post_id: int) -> None:
        repo = PostRepository(info.context.session)
        post = await repo.get_by_id(post_id)
        if post:
            await repo.delete(post)


schema = Schema(query=Query, mutation=Mutation)
