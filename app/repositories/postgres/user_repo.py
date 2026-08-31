from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any

from repositories.postgres.base_repo import BaseRepo
from models import User


class UserRepo(BaseRepo[User]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_username(
        self,
        username: str
    ) -> User | None:
        return await self.get_one_by_conditions(
            User.username == username
        )
    
    async def create(
        self,
        user_data: dict[str, Any]
    ) -> User:
        new_user = User(**user_data)
        
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        
        return new_user
