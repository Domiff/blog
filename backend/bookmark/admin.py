from backend.admin.base import BaseAdmin
from backend.bookmark.models import PostBookmark


class BookmarkAdmin(BaseAdmin, model=PostBookmark):
    column_list = [
        PostBookmark.id,
        PostBookmark.owner,
        PostBookmark.post,
        PostBookmark.created_at,
    ]
    column_details_list = [
        PostBookmark.id,
        PostBookmark.owner,
        PostBookmark.owner_id,
        PostBookmark.post,
        PostBookmark.post_id,
        PostBookmark.created_at,
        PostBookmark.updated_at,
    ]
    column_labels = {
        PostBookmark.id: "Unique identifier",
        PostBookmark.owner: "Owner",
        PostBookmark.owner_id: "Owner ID",
        PostBookmark.post: "Post",
        PostBookmark.post_id: "Post ID",
        PostBookmark.created_at: "Created at",
        PostBookmark.updated_at: "Updated at",
    }
    column_searchable_list = [
        PostBookmark.owner_id,
        PostBookmark.post_id,
    ]
    column_sortable_list = [
        PostBookmark.id,
        PostBookmark.created_at,
    ]
    form_columns = [
        PostBookmark.owner,
        PostBookmark.post,
    ]
    can_edit = False

    icon = "fa-solid fa-bookmark"
    category = "Bookmarks"
    category_icon = "fa-solid fa-star"

    name = "Post bookmark"
    name_plural = "Post bookmarks"
