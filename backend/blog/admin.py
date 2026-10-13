from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action, Flash

from backend.admin.base import BaseAdmin
from backend.admin.utils import truncate
from backend.blog.models import Comment, Post
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


class CommentAdmin(BaseAdmin, model=Comment):
    column_list = [
        Comment.id,
        Comment.body,
        Comment.post,
        Comment.author,
        Comment.created_at,
    ]
    column_details_list = [
        Comment.id,
        Comment.body,
        Comment.post,
        Comment.author,
        Comment.created_at,
        Comment.updated_at,
    ]
    column_labels = {
        Comment.id: "Unique identifier",
        Comment.body: "Body",
        Comment.post: "Post",
        Comment.author: "Author",
        Comment.created_at: "Created at",
        Comment.updated_at: "Updated at",
    }
    column_searchable_list = [
        Comment.body,
    ]
    column_sortable_list = [
        Comment.id,
        Comment.created_at,
    ]
    column_formatters = {
        Comment.body: truncate(),
    }

    form_edit_rules = [
        "body",
    ]

    icon = "fa-solid fa-comments"
    category = "Blog"
    category_icon = "fa-solid fa-rss"

    name = "Comment"
    name_plural = "Comments"
