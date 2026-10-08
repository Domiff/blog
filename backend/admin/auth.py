from fastapi import Request
from pwdlib.exceptions import UnknownHashError
from sqladmin.authentication import AuthenticationBackend

from backend.auth.utils import verify_password

from backend.auth.models import User
from backend.auth.repository import UserRepository
from backend.core.database import session_maker


class AdminAuth(AuthenticationBackend):
    @staticmethod
    async def _get_account(email: str) -> User | None:
        if not email:
            return None

        async with session_maker() as session:
            return await UserRepository(session).get_by_email(email)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("email", ""))
        password = str(form.get("password", ""))

        account = await self._get_account(email)

        if account is None or not account.is_active or not account.is_superuser:
            return False

        try:
            is_valid = verify_password(password, account.password)
        except UnknownHashError:
            return False

        if not is_valid:
            return False

        request.session.update({"user": account.email})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        account = await self._get_account(request.session.get("user", ""))
        return bool(account and account.is_active)
