from collections.abc import Sequence
from typing import Any

from sqlalchemy import select

from backend.core.database import BaseRepository
from backend.profile.models import Profile


class ProfileRepository(BaseRepository):
    async def create(self, data: dict[str, Any]) -> Profile:
        profile = Profile(**data)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def list(self) -> Sequence[Profile]:
        query = select(Profile)
        profiles = await self.session.scalars(query)
        return profiles.all()

    async def get_by_id(self, id: int) -> Profile | None:
        return await self.session.get(Profile, id)

    async def get_by_username(self, username: str) -> Profile | None:
        query = select(Profile).where(Profile.username == username)
        return await self.session.scalar(query)

    async def update(self, profile: Profile, data: dict[str, Any]) -> Profile:
        for key, value in data.items():
            if not hasattr(Profile, key):
                raise AttributeError(f"Profile has no field {key!r}")
            if value is None:
                continue
            setattr(profile, key, value)
        await self.session.flush()
        return profile

    async def delete(self, profile: Profile) -> None:
        await self.session.delete(profile)
        await self.session.flush()
