from fastapi import HTTPException
from http import HTTPStatus


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=HTTPStatus.CONFLICT, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=HTTPStatus.FORBIDDEN, detail=detail)
