from typing import Annotated

from authx import TokenPayload
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.auth.security import auth
from backend.auth.service import AuthService
from backend.core.depends import SessionDep

bearer = HTTPBearer()


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


TokenPayloadDep = Annotated[TokenPayload, Depends(auth.refresh_token_required)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
BearerDep = Annotated[HTTPAuthorizationCredentials, Security(bearer)]
