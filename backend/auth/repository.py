from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.models import User
from backend.core.database import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, data: dict[str, Any]) -> User:
        user = User(**data)
        self.session.add(user)
        await self.session.flush()
        return user

    async def list(self) -> Sequence[User]:
        query = select(User).order_by(User.id)
        users = await self.session.scalars(query)
        return users.all()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return await self.session.scalar(query)

    async def get_by_id(self, id: int) -> User | None:
        return await self.session.get(User, id)

    async def update(self, user: User, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if not hasattr(User, key):
                raise AttributeError(f"User has no field {key!r}")
            setattr(user, key, value)
        await self.session.flush()

    async def delete(self, user: User, is_soft: bool) -> None:
        if is_soft:
            await self.update(user, {"is_active": False})
        else:
            await self.session.delete(user)
            await self.session.flush()
