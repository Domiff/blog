from graphql import GraphQLError


class GraphQLAppError(GraphQLError):
    CODE = "INTERNAL_ERROR"
    MESSAGE = "Application error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.MESSAGE, extensions={"code": self.CODE})


class PermissionDenied(GraphQLAppError):
    CODE = "FORBIDDEN"
    MESSAGE = "You do not have permission to perform this action"


class NotFound(GraphQLAppError):
    CODE = "NOT_FOUND"
    MESSAGE = "Not found"
