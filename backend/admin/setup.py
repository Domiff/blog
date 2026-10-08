from fastapi import FastAPI, Request
from sqladmin import Admin, I18nConfig
from sqladmin._menu import CategoryMenu

from backend.admin.auth import AdminAuth
from backend.core.settings import BASE_DIR, settings
from backend.core.database import session_maker


def _category_is_visible(self: CategoryMenu, request: Request) -> bool:
    return any(
        child.is_visible(request) and child.is_accessible(request)
        for child in self.children
    )


def setup_admin(app: FastAPI) -> Admin:
    CategoryMenu.is_visible = _category_is_visible

    admin = Admin(
        app,
        session_maker=session_maker,
        base_url=settings.admin.ADMIN_BASE_URL,
        title=settings.app.APP_NAME,
        templates_dir=str(BASE_DIR / "templates"),
        static_files_kwargs={"directory": BASE_DIR / "static"},
        authentication_backend=AdminAuth(
            secret_key=settings.admin.ADMIN_SECRET_KEY,
            https_only=not settings.app.IS_DEBUG,
        ),
        i18n_config=I18nConfig(
            default_locale="en",
            language_switcher=["en", "ru"],
        ),
    )
    return admin
