from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action, Flash
from sqladmin.filters import BooleanFilter

from backend.admin.base import BaseAdmin
from backend.auth.models import User
from backend.auth.repository import UserRepository
from backend.core.database import session_maker
from backend.auth.utils import hash_password


class UserAdmin(BaseAdmin, model=User):
    column_list = [
        User.id,
        User.email,
        User.is_active,
        User.is_superuser,
    ]
    column_details_list = [
        User.id,
        User.email,
        User.is_active,
        User.is_superuser,
        User.created_at,
        User.updated_at,
    ]
    column_labels = {
        User.id: "Unique identifier",
        User.email: "Email",
        User.password: "Password",
        User.is_active: "Status",
        User.is_superuser: "Administrator",
        User.created_at: "Created at",
        User.updated_at: "Updated at",
    }
    column_searchable_list = [
        User.email,
    ]
    column_sortable_list = [
        User.id,
        User.email,
        User.is_active,
        User.created_at,
        User.updated_at,
    ]
    column_filters = [
        BooleanFilter(User.is_active, title="Status"),
        BooleanFilter(User.is_superuser, title="Administrator"),
    ]

    form_create_rules = [
        "email",
        "password",
        "is_active",
        "is_superuser",
    ]
    form_edit_rules = [
        "email",
        "is_active",
        "is_superuser",
    ]

    icon = "fa-solid fa-user-shield"
    category = "Access"
    category_icon = "fa-solid fa-lock"

    name = "User"
    name_plural = "Users"

    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request: Request
    ) -> None:
        if is_created:
            data["password"] = hash_password(data["password"])

    @action(
        name="change_status",
        label="Change status",
        confirmation_message="Are you sure?",
    )
    async def change_status(self, request: Request):
        pks = [pk for pk in request.query_params.get("pks", "").split(",") if pk]

        async with session_maker() as session:
            user_repo = UserRepository(session)
            for pk in pks:
                user = await user_repo.get_by_id(int(pk))
                if user is not None:
                    await user_repo.update(user, {"is_active": not user.is_active})
            await session.commit()

        Flash.success(request, "Statuses changed successfully")

        return RedirectResponse(request.url_for("admin:list", identity=self.identity))
