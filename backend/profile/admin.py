from backend.admin.base import BaseAdmin
from backend.admin.utils import truncate
from backend.profile.models import Profile


class ProfileAdmin(BaseAdmin, model=Profile):
    column_list = [
        Profile.id,
        Profile.username,
        Profile.user,
        Profile.created_at,
    ]
    column_details_list = [
        Profile.id,
        Profile.username,
        Profile.bio,
        Profile.user,
        Profile.created_at,
        Profile.updated_at,
    ]
    column_labels = {
        Profile.id: "Unique identifier",
        Profile.username: "Username",
        Profile.bio: "Bio",
        Profile.user: "User",
        Profile.created_at: "Created at",
        Profile.updated_at: "Updated at",
    }
    column_searchable_list = [
        Profile.username,
    ]
    column_sortable_list = [
        Profile.id,
        Profile.username,
        Profile.created_at,
    ]
    column_formatters = {
        Profile.bio: truncate(),
    }

    form_edit_rules = [
        "username",
        "bio",
    ]

    can_create = False
    can_delete = False

    icon = "fa-solid fa-id-card"
    category = "Access"
    category_icon = "fa-solid fa-lock"

    name = "Profile"
    name_plural = "Profiles"
