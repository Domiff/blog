from typing import Annotated

from authx import TokenPayload
from authx.exceptions import RevokedTokenError
from fastapi import Depends, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.auth.models import User
from backend.auth.repository import UserRepository
from backend.auth.security import auth
from backend.auth.service import AuthService
from backend.core.depends import SessionDep

bearer = HTTPBearer()


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


async def get_current_user(request: Request, session: SessionDep) -> User | None:
    token = await auth.get_token_from_request(request, optional=True)
    if token is None:
        return None
    if await auth.is_token_in_blocklist(token.token):
        raise RevokedTokenError("Token has been revoked")
    payload = auth.verify_token(token, verify_csrf=False)
    user = await UserRepository(session).get_by_id(int(payload.sub))
    if user is None or not user.is_active:
        return None
    return user


CurrentUserDep = Annotated[User | None, Depends(get_current_user)]
TokenPayloadDep = Annotated[TokenPayload, Depends(auth.refresh_token_required)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
BearerDep = Annotated[HTTPAuthorizationCredentials, Security(bearer)]
