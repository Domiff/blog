from dataclasses import dataclass
from functools import partial

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from backend.profile.models import Profile
from backend.profile.repository import ProfileRepository


@dataclass
class ProfileLoaders:
    profile_by_id: DataLoader[int, Profile]


async def load_profiles_by_id(
    session: AsyncSession, profile_ids: list[int]
) -> list[Profile]:
    profiles = await ProfileRepository(session).list_by_ids(profile_ids)
    by_id = {profile.id: profile for profile in profiles}
    return [by_id[profile_id] for profile_id in profile_ids]


def create_profile_loaders(session: AsyncSession) -> ProfileLoaders:
    return ProfileLoaders(
        profile_by_id=DataLoader(load_fn=partial(load_profiles_by_id, session)),
    )
