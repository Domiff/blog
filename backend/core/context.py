from strawberry.fastapi import BaseContext
from strawberry.extensions import SchemaExtension
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.depends import CurrentUserDep
from backend.core.depends import SessionDep
from backend.profile.models import Profile
from backend.profile.repository import ProfileRepository


class RollbackOnErrorExtension(SchemaExtension):
    async def on_execute(self):
        yield
        result = self.execution_context.result
        if result is not None and result.errors:
            await self.execution_context.context.session.rollback()


class SessionContext(BaseContext):
    def __init__(self, session: AsyncSession, profile: Profile | None) -> None:
        super().__init__()
        self.session = session
        self.profile = profile


async def get_context(session: SessionDep, user: CurrentUserDep) -> SessionContext:
    profile = None
    if user is not None:
        profile = await ProfileRepository(session).get_by_user_id(user.id)
    return SessionContext(session=session, profile=profile)
