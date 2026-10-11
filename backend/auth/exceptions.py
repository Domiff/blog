from backend.core.exceptions.rest import AppException


class Forbidden(AppException):
    DETAIL = "Forbidden"
    STATUS_CODE = 403


class Unauthorized(AppException):
    DETAIL = "Unauthorized"
    STATUS_CODE = 401
