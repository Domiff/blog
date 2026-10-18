from typing import Protocol

import strawberry
from sqlalchemy.orm import Mapped

from backend.core.exceptions.graphql import NotFound, PermissionDenied


class Owner(Protocol):
    owner_id: Mapped[int]


def require_owner[T: Owner](obj: T | None, info: strawberry.Info, name: str) -> T:
    if obj is None:
        raise NotFound(f"{name} not found")
    if obj.owner_id != info.context.profile.id:
        raise PermissionDenied()
    return obj
