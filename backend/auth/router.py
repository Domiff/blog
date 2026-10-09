from fastapi import APIRouter, status

from backend.auth.depends import AuthServiceDep, BearerDep, TokenPayloadDep
from backend.auth.schemas import CredentialsSchema, LogoutSchema


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: CredentialsSchema, service: AuthServiceDep
):
    return await service.register(data)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: CredentialsSchema, service: AuthServiceDep):
    return await service.login(data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: LogoutSchema, bearer: BearerDep, service: AuthServiceDep
) -> None:
    await service.logout(bearer.credentials, data.refresh)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(payload: TokenPayloadDep, service: AuthServiceDep):
    return await service.refresh(payload)
