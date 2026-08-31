from fastapi import (
    Request,
    Response
)

from services import (
    UserService,
    SessionService
)
from schemas import (
    UserCreate,
    UserShortResponse,
    LoginRequest,
    SessionResponse
)
from models import User
from core import exceptions


class AuthService:
    user_service: UserService
    session_service: SessionService

    def __init__(
        self,
        user_service: UserService,
        session_service: SessionService
    ) -> None:
        self.user_service = user_service
        self.session_service = session_service

    async def register(
        self,
        user_data: UserCreate
    ) -> UserShortResponse:
        return await self.user_service.create_user(
            user_data
        )
    
    async def _get_user_for_auth(
        self,
        username: str
    ) -> User:
        try:
            user = await self.user_service.get_short_by_username(
                username,
                raw_model=True
            )
            return user
        except exceptions.NotFoundException as e:
            raise exceptions.InvalidCredentialsException(
                'Invalid username or password'
            )
    
    def _verify_password(
        self,
        user: User,
        password: str
    ) -> None:
        is_valid = self.user_service.verify_password(
            user,
            password
        )

        if not is_valid:
            raise exceptions.InvalidCredentialsException(
                'Invalid username or password'
            )

    async def login(
        self,
        login_data: LoginRequest,
        request: Request,
        response: Response
    ) -> SessionResponse:
        user = await self._get_user_for_auth(
            login_data.username
        )

        self._verify_password(user, login_data.password)
        
        session = await self.session_service.create_session(
            user,
            request,
            response
        )

        return session
    
    async def logout(
        self,
        session_id: str,
        response: Response
    ) -> bool:
        return await self.session_service.delete_session(
            session_id=session_id,
            response=response
        )