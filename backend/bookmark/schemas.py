from typing import Annotated, TYPE_CHECKING

import strawberry

from backend.bookmark.models import PostBookmark
from backend.bookmark.repository import PostBookmarkRepository
from backend.blog.repository import PostRepository
from backend.core.exceptions.graphql import NotFound
from backend.core.permissions import IsAuthenticated

if TYPE_CHECKING:
    from backend.blog.schemas import PostType


@strawberry.input
class CreateBookmarkInput:
    post_id: int


@strawberry.type(name="PostBookmark")
class BookmarkType:
    id: int
    post_id: strawberry.Private[int]
    owner_id: strawberry.Private[int]

    @strawberry.field
    async def post(
        self, info: strawberry.Info
    ) -> Annotated["PostType", strawberry.lazy("backend.blog.schemas")]:
        from backend.blog.schemas import PostType

        post = await info.context.blog_loaders.post_by_id.load(self.post_id)
        return PostType.from_model(post)

    @classmethod
    def from_model(cls, bookmark: PostBookmark) -> "BookmarkType":
        return cls(
            id=bookmark.id,
            post_id=bookmark.post_id,
            owner_id=bookmark.owner_id,
        )


@strawberry.type
class BookmarkQuery:
    @strawberry.field
    async def bookmarks(
        self, info: strawberry.Info, owner_id: int
    ) -> list[BookmarkType]:
        repo = PostBookmarkRepository(info.context.session)
        bookmarks = await repo.list_by_owner(owner_id)
        return [BookmarkType.from_model(bookmark) for bookmark in bookmarks]


@strawberry.type
class BookmarkMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_bookmark(
        self, info: strawberry.Info, input: CreateBookmarkInput
    ) -> BookmarkType:
        if not await PostRepository(info.context.session).get_by_id(input.post_id):
            raise NotFound("Post not found")

        repo = PostBookmarkRepository(info.context.session)
        existing_bookmark = await repo.get_by_owner_and_post(
            owner_id=info.context.profile.id, post_id=input.post_id
        )

        if existing_bookmark:
            return BookmarkType.from_model(existing_bookmark)

        input_as_dict = strawberry.asdict(input)
        input_as_dict["owner_id"] = info.context.profile.id
        bookmark = await repo.create(input_as_dict)
        return BookmarkType.from_model(bookmark)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def delete_bookmark(self, info: strawberry.Info, post_id: int) -> None:
        repo = PostBookmarkRepository(info.context.session)
        bookmark = await repo.get_by_owner_and_post(
            owner_id=info.context.profile.id, post_id=post_id
        )
        if bookmark is None:
            raise NotFound("PostBookmark not found")
        await repo.delete(bookmark)
