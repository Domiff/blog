from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.admin.setup import setup_admin
from backend.auth.admin import UserAdmin
from backend.auth.security import auth
from backend.auth.router import router as auth_router
from backend.blog.admin import PostAdmin
from backend.blog.router import router as blog_router
from backend.core.settings import settings
from backend.core.health import router as health_router
from backend.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application")

    yield

    logger.info("Stopping application")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app.APP_TITLE,
        version=settings.app.APP_VERSION,
        lifespan=lifespan,
        openapi_url="/openapi.json" if settings.app.IS_DEBUG else None,
    )
    auth.handle_errors(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.CORS_ORIGINS,
        allow_credentials=settings.cors.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.cors.CORS_ALLOW_METHODS,
        allow_headers=settings.cors.CORS_ALLOW_HEADERS,
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(blog_router)

    admin = setup_admin(app)
    admin.add_view(UserAdmin)
    admin.add_view(PostAdmin)

    return app
