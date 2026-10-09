from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action, Flash

from backend.admin.base import BaseAdmin
from backend.admin.utils import truncate
from backend.blog.models import Post
from backend.blog.repository import PostRepository
from backend.core.database import session_maker


class PostAdmin(BaseAdmin, model=Post):
    column_list = [
        Post.id,
        Post.title,
        Post.created_at,
        Post.updated_at,
    ]
    column_details_list = [
        Post.id,
        Post.title,
        Post.body,
        Post.created_at,
        Post.updated_at,
    ]
    column_labels = {
        Post.id: "Unique identifier",
        Post.title: "Title",
        Post.body: "Body",
        Post.created_at: "Created at",
        Post.updated_at: "Updated at",
    }
    column_searchable_list = [
        Post.title,
        Post.body,
    ]
    column_sortable_list = [
        Post.id,
        Post.title,
        Post.created_at,
        Post.updated_at,
    ]
    column_formatters = {
        Post.title: truncate(),
        Post.body: truncate(),
    }

    form_create_rules = [
        "title",
        "body",
    ]
    form_edit_rules = [
        "title",
        "body",
    ]

    icon = "fa-solid fa-newspaper"
    category = "Blog"
    category_icon = "fa-solid fa-rss"

    name = "Post"
    name_plural = "Posts"
