from datetime import timedelta

from authx import AuthX, AuthXConfig

from backend.core.settings import settings

config = AuthXConfig(
    JWT_ALGORITHM=settings.auth.JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=settings.auth.JWT_ACCESS_TOKEN_EXPIRES),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(hours=settings.auth.JWT_REFRESH_TOKEN_EXPIRES),
    JWT_TOKEN_LOCATION=["headers"],
    JWT_PRIVATE_KEY=settings.auth.JWT_PRIVATE_KEY.read_text(),
    JWT_PUBLIC_KEY=settings.auth.JWT_PUBLIC_KEY.read_text(),
)
auth = AuthX(config=config)
