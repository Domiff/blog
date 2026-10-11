from datetime import datetime
from typing import Annotated, TYPE_CHECKING

import strawberry

from backend.blog.enums import PostStatus
from backend.blog.repository import PostRepository
from backend.blog.models import Post
from backend.core.exceptions.graphql import PermissionDenied, NotFound
from backend.core.permissions import IsAuthenticated
from backend.profile.repository import ProfileRepository


if TYPE_CHECKING:
    from backend.profile.schemas import ProfileType


@strawberry.input
class CreatePostInput:
    title: str
    body: str


@strawberry.input
class UpdatePostInput:
    title: str | None
    body: str | None


@strawberry.type(name="Post")
class PostType:
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    status: PostStatus
    author_id: strawberry.Private[int]

    @strawberry.field
    async def author(
        self, info: strawberry.Info
    ) -> Annotated["ProfileType", strawberry.lazy("backend.profile.schemas")]:
        from backend.profile.schemas import ProfileType

        profile = await ProfileRepository(info.context.session).get_by_id(self.author_id)
        return ProfileType.from_model(profile)

    @classmethod
    def from_model(cls, post: Post) -> "PostType":
        return cls(
            id=post.id,
            title=post.title,
            body=post.body,
            created_at=post.created_at,
            updated_at=post.updated_at,
            status=post.status,
            published_at=post.published_at,
            author_id=post.author_id,
        )


@strawberry.type
class BlogQuery:
    @strawberry.field
    async def posts(self, info: strawberry.Info) -> list[PostType] | None:
        repo = PostRepository(info.context.session)
        posts = await repo.list()
        if not posts:
            return None
        return [PostType.from_model(post) for post in posts]

    @strawberry.field
    async def post_by_id(self, info: strawberry.Info, post_id: int) -> PostType | None:
        repo = PostRepository(info.context.session)
        post = await repo.get_by_id(post_id)
        if not post:
            return None
        return PostType.from_model(post)


@strawberry.type
class BlogMutation:
    @staticmethod
    def _get_own_post(post: Post | None, info: strawberry.Info) -> Post:
        if post is None:
            raise NotFound("Post not found")
        if post.author_id != info.context.profile.id:
            raise PermissionDenied()
        return post

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_post(self, info: strawberry.Info, input: CreatePostInput) -> PostType:
        repo = PostRepository(info.context.session)
        input_as_dict = strawberry.asdict(input)
        input_as_dict["author_id"] = info.context.profile.id
        post = await repo.create(input_as_dict)
        return PostType.from_model(post)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_post(
        self, info: strawberry.Info, post_id: int, input: UpdatePostInput
    ) -> PostType:
        repo = PostRepository(info.context.session)
        post = BlogMutation._get_own_post(await repo.get_by_id(post_id), info)
        post = await repo.update(post, strawberry.asdict(input))
        return PostType.from_model(post)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def delete_post(self, info: strawberry.Info, post_id: int) -> None:
        repo = PostRepository(info.context.session)
        post = BlogMutation._get_own_post(await repo.get_by_id(post_id), info)
        await repo.delete(post)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def publish_post(self, info: strawberry.Info, post_id: int) -> PostType | None:
        repo = PostRepository(info.context.session)
        post = BlogMutation._get_own_post(await repo.get_by_id(post_id), info)
        if post.status != PostStatus.DRAFT:
            return None
        return PostType.from_model(await repo.publish(post))
