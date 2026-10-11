import strawberry
from strawberry.tools import merge_types

from backend.blog.schemas import BlogQuery, BlogMutation
from backend.core.context import RollbackOnErrorExtension
from backend.profile.schemas import ProfileQuery, ProfileMutation


Query = merge_types("Query", (BlogQuery, ProfileQuery))
Mutation = merge_types("Mutation", (BlogMutation, ProfileMutation))

schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=[RollbackOnErrorExtension])
