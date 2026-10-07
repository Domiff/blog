from fastapi import APIRouter

from backend.core.database import ping_database

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict[str, bool | str]:
    database = await ping_database()

    return {
        "status": "Good" if database else "Bad",
        "database": database,
    }
