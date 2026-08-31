from fastapi import (
    APIRouter,
    Depends,
    status,
    Body,
    Response,
    Request
)

from typing import Annotated

from core.dependencies import (
    AuthServiceDep,
    CurrentUserDep,
    SessionIdDep,
    require_role
)
from schemas import (
    UserShortResponse,
    UserCreate,
    SessionResponse,
    LoginRequest,
    SessionUser
)
from models.users import UserRole


router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@router.post(
    '/register',
    response_model=UserShortResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    auth_service: AuthServiceDep,
    user_data: Annotated[UserCreate, Body()],
    _: SessionUser = Depends(
        require_role(UserRole.SUPERUSER)
    )
):
    return await auth_service.register(user_data)


@router.post(
    '/login',
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    login_data: Annotated[LoginRequest, Body()],
    auth_service: AuthServiceDep,
    request: Request,
    response: Response
):
    return await auth_service.login(
        login_data=login_data,
        request=request,
        response=response
    )


@router.get(
    '/logout',
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    _: CurrentUserDep,
    session_id: SessionIdDep,
    auth_service: AuthServiceDep,
    response: Response
):
    await auth_service.logout(session_id, response)


@router.get(
    '/me',
    response_model=UserShortResponse,
    status_code=status.HTTP_200_OK
)
def me(
    user: CurrentUserDep
):
    return user
