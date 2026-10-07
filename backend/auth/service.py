from authx import TokenPayload, TokenResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.exceptions import Unauthorized
from backend.auth.repository import UserRepository
from backend.auth.schemas import CredentialsSchema
from backend.auth.security import auth
from backend.auth.utils import hash_password, verify_password
from backend.core.exceptions import AlreadyExists
from backend.core.logging import get_logger

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

    async def refresh(self, payload: TokenPayload) -> TokenResponse:
        user = await self.repo.get_by_id(int(payload.sub))
        if user is None or not user.is_active:
            logger.warning("Refresh failed: user unavailable", extra={"user_id": payload.sub})
            raise Unauthorized("Invalid token")
        logger.info("Tokens refreshed", extra={"user_id": user.id})
        return self._authenticate(user.id)
