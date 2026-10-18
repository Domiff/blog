from datetime import datetime
from typing import Annotated, TYPE_CHECKING

import strawberry
from strawberry.tools import merge_types

from backend.blog.enums import PostStatus
from backend.blog.repository import PostRepository, CommentRepository
from backend.blog.models import Post, Comment
from backend.blog.permissions import require_owner
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

        profile = await info.context.profile_loaders.profile_by_id.load(self.author_id)
        return ProfileType.from_model(profile)

    @strawberry.field
    async def comments(self, info: strawberry.Info) -> list["CommentType"]:
        comments = await info.context.blog_loaders.comments_by_post.load(self.id)
        return [CommentType.from_model(comment) for comment in comments]

    @strawberry.field
    async def comments_count(self, info: strawberry.Info) -> int:
        return await info.context.blog_loaders.comments_count_by_post.load(self.id)

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


@strawberry.input
class CreateCommentInput:
    body: str
    post_id: int


@strawberry.input
class UpdateCommentInput:
    body: str


@strawberry.type(name="Comment")
class CommentType:
    id: int
    body: str
    created_at: datetime
    updated_at: datetime
    author_id: strawberry.Private[int]

    @strawberry.field
    async def author(
        self, info: strawberry.Info
    ) -> Annotated["ProfileType", strawberry.lazy("backend.profile.schemas")]:
        from backend.profile.schemas import ProfileType

        profile = await info.context.profile_loaders.profile_by_id.load(self.author_id)
        return ProfileType.from_model(profile)

    @classmethod
    def from_model(cls, comment: Comment) -> "CommentType":
        return cls(
            id=comment.id,
            body=comment.body,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author_id=comment.author_id,
        )


@strawberry.type
class PostQuery:
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
        if post is None:
            return None
        profile = info.context.profile
        is_author = profile is not None and post.author_id == profile.id
        if post.status != PostStatus.PUBLISHED and not is_author:
            return None
        return PostType.from_model(post)

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def my_posts(
        self, info: strawberry.Info, status: PostStatus | None = None
    ) -> list[PostType]:
        repo = PostRepository(info.context.session)
        posts = await repo.list_by_author(info.context.profile.id, status)
        return [PostType.from_model(post) for post in posts]


@strawberry.type
class PostMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_post(
        self, info: strawberry.Info, input: CreatePostInput
    ) -> PostType:
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
        post = require_owner(await repo.get_by_id(post_id), info, "Post")
        post = await repo.update(post, strawberry.asdict(input))
        return PostType.from_model(post)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def delete_post(self, info: strawberry.Info, post_id: int) -> None:
        repo = PostRepository(info.context.session)
        post = require_owner(await repo.get_by_id(post_id), info, "Post")
        await repo.delete(post)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def publish_post(
        self, info: strawberry.Info, post_id: int
    ) -> PostType | None:
        repo = PostRepository(info.context.session)
        post = require_owner(await repo.get_by_id(post_id), info, "Post")
        if post.status != PostStatus.DRAFT:
            return None
        return PostType.from_model(await repo.publish(post))


@strawberry.type
class CommentQuery:
    @strawberry.field
    async def comment_by_id(
        self, info: strawberry.Info, comment_id: int
    ) -> CommentType | None:
        repo = CommentRepository(info.context.session)
        comment = await repo.get_by_id(comment_id)
        if not comment:
            return None
        return CommentType.from_model(comment)


@strawberry.type
class CommentMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_comment(
        self, info: strawberry.Info, input: CreateCommentInput
    ) -> CommentType:
        post_repo = PostRepository(info.context.session)
        post = await post_repo.get_by_id(input.post_id)

        if not post:
            raise NotFound("Post not found")

        if post.status != PostStatus.PUBLISHED:
            raise NotFound("Published post not found")

        comment_repo = CommentRepository(info.context.session)
        input_as_dict = strawberry.asdict(input)
        input_as_dict["author_id"] = info.context.profile.id
        comment = await comment_repo.create(input_as_dict)
        return CommentType.from_model(comment)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_comment(
        self, info: strawberry.Info, comment_id: int, input: UpdateCommentInput
    ) -> CommentType:
        repo = CommentRepository(info.context.session)
        comment = require_owner(await repo.get_by_id(comment_id), info, "Comment")
        comment = await repo.update(comment, strawberry.asdict(input))
        return CommentType.from_model(comment)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def delete_comment(self, info: strawberry.Info, comment_id: int) -> None:
        repo = CommentRepository(info.context.session)
        comment = require_owner(await repo.get_by_id(comment_id), info, "Comment")
        await repo.delete(comment)


BlogQuery = merge_types("BlogQuery", (PostQuery, CommentQuery))
BlogMutation = merge_types("BlogMutation", (PostMutation, CommentMutation))
