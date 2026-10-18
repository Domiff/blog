from typing import Annotated, TYPE_CHECKING

import strawberry

from backend.core.permissions import IsAuthenticated
from backend.profile.models import Profile
from backend.profile.repository import ProfileRepository

if TYPE_CHECKING:
    from backend.blog.schemas import PostType
    from backend.bookmark.schemas import BookmarkType


@strawberry.input
class UpdateProfileInput:
    username: str | None
    bio: str | None


@strawberry.type(name="Profile")
class ProfileType:
    id: int
    username: str
    bio: str | None

    @strawberry.field
    async def posts(
        self, info: strawberry.Info
    ) -> list[Annotated["PostType", strawberry.lazy("backend.blog.schemas")]]:
        from backend.blog.schemas import PostType

        posts = await info.context.blog_loaders.posts_by_author.load(self.id)
        return [PostType.from_model(post) for post in posts]

    @strawberry.field
    async def posts_count(
        self, info: strawberry.Info
    ) -> int:
        return await info.context.blog_loaders.posts_count_by_author.load(self.id)

    @strawberry.field
    async def bookmarks(self, info: strawberry.Info)-> list[Annotated["BookmarkType", strawberry.lazy("backend.bookmark.schemas")]]:
        from backend.bookmark.schemas import BookmarkType

        bookmarks = await info.context.bookmark_loaders.bookmarks_by_owner.load(self.id)
        return [BookmarkType.from_model(bookmark) for bookmark in bookmarks]

    @strawberry.field
    async def bookmarks_count(self, info: strawberry.Info) -> int:
        return await info.context.bookmark_loaders.bookmarks_count_by_owner.load(self.id)

    @classmethod
    def from_model(cls, profile: Profile) -> "ProfileType":
        return cls(
            id=profile.id,
            username=profile.username,
            bio=profile.bio,
        )


@strawberry.type
class ProfileQuery:
    @strawberry.field
    async def profiles(self, info: strawberry.Info) -> list[ProfileType] | None:
        repo = ProfileRepository(info.context.session)
        profiles = await repo.list()
        if not profiles:
            return None
        return [ProfileType.from_model(profile) for profile in profiles]

    @strawberry.field
    async def profile_by_id(
        self, info: strawberry.Info, profile_id: int
    ) -> ProfileType | None:
        repo = ProfileRepository(info.context.session)
        profile = await repo.get_by_id(profile_id)
        if not profile:
            return None
        return ProfileType.from_model(profile)

    @strawberry.field
    async def profile_by_username(
        self, info: strawberry.Info, username: str
    ) -> ProfileType | None:
        repo = ProfileRepository(info.context.session)
        profile = await repo.get_by_username(username)
        if not profile:
            return None
        return ProfileType.from_model(profile)


@strawberry.type
class ProfileMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_profile(
        self, info: strawberry.Info, input: UpdateProfileInput
    ) -> ProfileType:
        repo = ProfileRepository(info.context.session)
        profile = await repo.update(info.context.profile, strawberry.asdict(input))
        return ProfileType.from_model(profile)
