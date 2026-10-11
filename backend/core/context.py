from strawberry.fastapi import BaseContext
from strawberry.extensions import SchemaExtension
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.depends import SessionDep


class RollbackOnErrorExtension(SchemaExtension):
    async def on_execute(self):
        yield
        result = self.execution_context.result
        if result is not None and result.errors:
            await self.execution_context.context.session.rollback()


class SessionContext(BaseContext):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session


async def get_context(session: SessionDep) -> SessionContext:
    return SessionContext(session=session)
