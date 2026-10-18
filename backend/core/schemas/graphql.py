from functools import partial

import strawberry
from strawberry.extensions import MaskErrors
from strawberry.tools import merge_types

from backend.blog.schemas import BlogQuery, BlogMutation
from backend.bookmark.schemas import BookmarkQuery, BookmarkMutation
from backend.core.context import RollbackOnErrorExtension
from backend.core.exceptions.graphql import mask_error
from backend.profile.schemas import ProfileQuery, ProfileMutation

Query = merge_types("Query", (BlogQuery, ProfileQuery, BookmarkQuery))
Mutation = merge_types("Mutation", (BlogMutation, ProfileMutation, BookmarkMutation))

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        RollbackOnErrorExtension,
        partial(
            MaskErrors, should_mask_error=mask_error, error_message="Unexpected error."
        ),
    ],
)
