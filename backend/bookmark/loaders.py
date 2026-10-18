from dataclasses import dataclass
from functools import partial

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from backend.bookmark.models import PostBookmark
from backend.bookmark.repository import PostBookmarkRepository


@dataclass
class BookmarkLoaders:
    bookmarks_by_owner: DataLoader[int, list[PostBookmark]]
    bookmarks_count_by_owner: DataLoader[int, int]


async def load_bookmarks_by_owner(
    session: AsyncSession, owner_ids: list[int]
) -> list[list[PostBookmark]]:
    bookmarks = await PostBookmarkRepository(session).list_by_owners(owner_ids)
    grouped: dict[int, list[PostBookmark]] = {owner_id: [] for owner_id in owner_ids}
    for bookmark in bookmarks:
        grouped[bookmark.owner_id].append(bookmark)
    return [grouped[owner_id] for owner_id in owner_ids]


async def load_bookmarks_count_by_owner(
    session: AsyncSession, owner_ids: list[int]
) -> list[int]:
    bookmarks_count = await PostBookmarkRepository(session).count_by_owners(owner_ids)
    return [bookmarks_count.get(owner_id, 0) for owner_id in owner_ids]


def create_bookmark_loaders(session: AsyncSession) -> BookmarkLoaders:
    return BookmarkLoaders(
        bookmarks_by_owner=DataLoader(
            load_fn=partial(load_bookmarks_by_owner, session)
        ),
        bookmarks_count_by_owner=DataLoader(
            load_fn=partial(load_bookmarks_count_by_owner, session)
        ),
    )
