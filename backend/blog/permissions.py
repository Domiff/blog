from typing import Protocol

import strawberry
from sqlalchemy.orm import Mapped

from backend.core.exceptions.graphql import NotFound, PermissionDenied


class Authored(Protocol):
    author_id: Mapped[int]


def require_owner[T: Authored](obj: T | None, info: strawberry.Info, name: str) -> T:
    if obj is None:
        raise NotFound(f"{name} not found")
    if obj.author_id != info.context.profile.id:
        raise PermissionDenied()
    return obj
