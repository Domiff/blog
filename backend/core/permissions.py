import strawberry


class IsAuthenticated(strawberry.BasePermission):
    message = "Authentication required"

    def has_permission(self, source, info: strawberry.Info, **kwargs) -> bool:
        return info.context.profile is not None
