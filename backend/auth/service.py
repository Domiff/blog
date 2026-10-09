import math
from datetime import timedelta

import jwt
from authx import RequestToken, TokenPayload, TokenResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.exceptions import Unauthorized
from backend.auth.repository import UserRepository
from backend.auth.schemas import CredentialsSchema
from backend.auth.security import auth
from backend.auth.utils import hash_password, verify_password
from backend.core.exceptions import AlreadyExists
from backend.core.logging import get_logger
from backend.core.redis import redis, key_builder
from backend.core.settings import settings

logger = get_logger(__name__)


class AuthService:
    _DUMMY_PASSWORD_HASH = hash_password("dummy")

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(self.session)

    @staticmethod
    def _authenticate(user_id: int) -> TokenResponse:
        return auth.create_token_pair(uid=str(user_id))

    async def register(self, credentials: CredentialsSchema) -> TokenResponse:
        data = {
            "email": credentials.email,
            "password": hash_password(credentials.password),
        }
        try:
            user = await self.repo.create(data)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("User already exists", extra={"email": credentials.email})
            raise AlreadyExists() from e
        logger.info("User created successfully", extra={"user_id": user.id})
        return self._authenticate(user.id)

    async def login(self, credentials: CredentialsSchema) -> TokenResponse:
        user = await self.repo.get_by_email(credentials.email)
        if user is None:
            verify_password(credentials.password, self._DUMMY_PASSWORD_HASH)
            logger.warning("Login failed: user does not exist", extra={"email": credentials.email})
            raise Unauthorized("Invalid credentials")
        if not verify_password(credentials.password, user.password):
            logger.warning("Login failed: password mismatch", extra={"user_id": user.id})
            raise Unauthorized("Invalid credentials")
        if not user.is_active:
            logger.warning("Login failed: user is inactive", extra={"user_id": user.id})
            raise Unauthorized("Invalid credentials")
        logger.info("User logged in", extra={"user_id": user.id})
        return self._authenticate(user.id)

    async def logout(self, access: str, refresh: str) -> None:
        refresh_token = RequestToken(token=refresh, location="json", type="refresh")
        refresh_payload = auth.verify_token(refresh_token, verify_csrf=False)

        try:
            access_payload = jwt.decode(
                access,
                auth.config.public_key,
                algorithms=[auth.config.JWT_ALGORITHM],
                options={"verify_exp": False},
            )
        except jwt.InvalidTokenError as e:
            logger.warning("Logout failed: invalid access token")
            raise Unauthorized("Invalid token") from e
        if (
            access_payload.get("type") != "access"
            or access_payload.get("sub") != refresh_payload.sub
        ):
            logger.warning(
                "Logout failed: token mismatch", extra={"user_id": refresh_payload.sub}
            )
            raise Unauthorized("Invalid token")

        await redis.set(
            key_builder("revoked", access),
            "1",
            timedelta(minutes=settings.auth.JWT_ACCESS_TOKEN_EXPIRES),
        )
        await redis.set(
            key_builder("revoked", refresh),
            "1",
            math.ceil(refresh_payload.time_until_expiry.total_seconds()),
        )
        logger.info("User logged out", extra={"user_id": refresh_payload.sub})

    async def refresh(self, payload: TokenPayload) -> TokenResponse:
        user = await self.repo.get_by_id(int(payload.sub))
        if user is None or not user.is_active:
            logger.warning("Refresh failed: user unavailable", extra={"user_id": payload.sub})
            raise Unauthorized("Invalid token")
        logger.info("Tokens refreshed", extra={"user_id": user.id})
        return self._authenticate(user.id)
