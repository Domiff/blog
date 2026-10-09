from pydantic import EmailStr

from backend.core.schemas import BaseSchema, UTCDatetime


class CredentialsSchema(BaseSchema):
    email: EmailStr
    password: str


class LogoutSchema(BaseSchema):
    refresh: str


class UserSchema(BaseSchema):
    password: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: UTCDatetime
    updated_at: UTCDatetime
