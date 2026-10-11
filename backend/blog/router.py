from strawberry.fastapi import GraphQLRouter

from backend.core.context import get_context
from backend.blog.schemas import schema

router = GraphQLRouter(
    schema=schema, prefix="/blog", tags=["Blog"], context_getter=get_context
)
