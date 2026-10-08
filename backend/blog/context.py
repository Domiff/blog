from fastapi import Depends
from strawberry.fastapi import BaseContext
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import session_maker


class SessionContext(BaseContext):
    def __init__(self, session) -> None:
        self.session = session


async def session_context_dependency():
    async with session_maker() as session:
        try:
            yield SessionContext(session=session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_context(
    session_context=Depends(session_context_dependency),
):
    return session_context
