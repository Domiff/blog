from datetime import timedelta

from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.core.settings import settings
from backend.core.redis import redis, key_builder

config = AuthXConfig(
    JWT_ALGORITHM=settings.auth.JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=settings.auth.JWT_ACCESS_TOKEN_EXPIRES),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=settings.auth.JWT_REFRESH_TOKEN_EXPIRES),
    JWT_TOKEN_LOCATION=["headers"],
    JWT_PRIVATE_KEY=settings.auth.JWT_PRIVATE_KEY.read_text(),
    JWT_PUBLIC_KEY=settings.auth.JWT_PUBLIC_KEY.read_text(),
)
auth = AuthX(config=config)


@auth.set_callback_token_blocklist
async def is_token_revoked(token: str) -> bool:
    return await redis.exists(key_builder("revoked", token)) > 0


def setup_auth_errors(app: FastAPI) -> None:
    auth.handle_errors(app)

    @app.exception_handler(JWTDecodeError)
    async def jwt_decode_error_handler(
        request: Request, exc: JWTDecodeError
    ) -> JSONResponse:
        name = exc.__class__.__name__
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": getattr(auth, f"MSG_{name}", None) or str(exc),
                "error_type": name,
            },
        )
