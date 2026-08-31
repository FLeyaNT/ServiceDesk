from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    message: str
    status_code: int
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,

    ) -> None:
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    
    def __init__(
        self,
        message: str = 'Resource not found'   
    ):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND
        )


class AlreadyExistsException(AppException):
    
    def __init__(
        self,
        message: str = 'Resource already exists'   
    ) -> None:
        super().__init__(
            message,
            status.HTTP_409_CONFLICT
        )


class InvalidCredentialsException(AppException):

    def __init__(
        self,
        message: str = 'Invalid credentials'
    ) -> None:
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(AppException):

    def __init__(
        self,
        message: str = 'Not enough rights'
    ) -> None:
        super().__init__(
            message,
            status.HTTP_403_FORBIDDEN
        )


class UnauthorizedException(AppException):

    def __init__(
        self,
        message: str = 'Not authorized'
    ) -> None:
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED
        )


class ConflictException(AppException):

    def __init__(
        self,
        message: str = 'Conflict'
    ):
        super().__init__(
            message,
            status.HTTP_409_CONFLICT
        )


def init_exceptions(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': exc.message}
        )
