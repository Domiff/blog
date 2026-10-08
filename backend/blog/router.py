from strawberry.fastapi import GraphQLRouter

from backend.blog.context import get_context
from backend.blog.schemas import schema

router = GraphQLRouter(
    schema=schema, prefix="/graphql", tags=["Blog"], context_getter=get_context
)
