from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Select,
    ColumnElement
)

from typing import TypeVar, Generic, Any

from models.base_model import Base


ModelType = TypeVar('ModelType', bound=Base)


class BaseRepo(Generic[ModelType]):
    model: type[ModelType]
    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType]
    ):
        self.session = session
        self.model = model

    def _get_by(
        self,
        *conditions: ColumnElement[bool]
    ) -> Select[tuple[ModelType]]:
        stmt = select(self.model)

        if conditions:
            stmt = stmt.where(*conditions)

        return stmt
    
    async def get_one_by_conditions(
        self,
        *conditions: ColumnElement[bool],
    ) -> ModelType | None:
        stmt = self._get_by(*conditions)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_many_by_conditions(
        self,
        *conditions: ColumnElement[bool],
        order_by: Any | None = None,
        limit: int | None = None
    ) -> list[ModelType]:
        stmt = self._get_by(*conditions)

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        obj_id: int,
    ) -> ModelType | None:
        return await self.get_one_by_conditions(
            self.model.id == obj_id
        )
