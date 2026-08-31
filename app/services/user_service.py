from repositories.postgres.user_repo import UserRepo
from services import HashService
from schemas.user import (
    UserShortResponse,
    UserCreate
)
from core import exceptions
from models import User


class UserService:
    user_repo: UserRepo
    hash_service: HashService

    def __init__(
        self,
        user_repo: UserRepo,
        hash_service: HashService
    ) -> None:
        self.user_repo = user_repo
        self.hash_service = hash_service

    async def get_short_by_id(
        self,
        user_id: int,
        raw_model: bool = False
    ) -> UserShortResponse | User:
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise exceptions.NotFoundException(
                'User not found'
            )
        
        if raw_model:
            return user
        
        return UserShortResponse.model_validate(user)
    
    async def exists_by_username(
        self,
        username: str
    ) -> bool:
        user = await self.user_repo.get_by_username(username)
        if not user:
            return False
        return True
    
    async def get_short_by_username(
        self,
        username: str,
        raw_model: bool = False
    ) -> UserShortResponse| User:
        user = await self.user_repo.get_by_username(username)

        if not user:
            raise exceptions.NotFoundException(
                'User not found'
            )
        
        if raw_model:
            return user
        
        return UserShortResponse.model_validate(user)
    
    async def create_user(
        self,
        user_data: UserCreate
    ) -> UserShortResponse:
        if await self.exists_by_username(user_data.username):
            raise exceptions.AlreadyExistsException(
                'User with this username already exists'
            )
        
        user_data_dict = user_data.model_dump()
        password = user_data_dict.pop('password')
        hashed_password = self.hash_service.hash_password(password)
        user_data_dict['hashed_password'] = hashed_password

        new_user = await self.user_repo.create(user_data_dict)

        return UserShortResponse.model_validate(new_user)
    
    def verify_password(
        self,
        user: User,
        password: str
    ) -> bool:
        return self.hash_service.verify_password(
            password,
            user.hashed_password
        )
