from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from models import (
    IssueType,
    inventory_issue_types
)
from .base_repo import BaseRepo


class IssueTypesRepo(BaseRepo[IssueType]):

    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        super().__init__(session, IssueType)

    async def get_by_inventory_type_id(
        self,
        invent_type_id: int
    ) -> list[IssueType]:
        stmt = (
            select(IssueType)
            .join(
                inventory_issue_types,
                IssueType.id == inventory_issue_types.c.issue_type_id
            )
            .where(
                inventory_issue_types.c.inventory_type_id 
                == invent_type_id
            )
            .order_by(IssueType.name.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def check_compatibility(
        self,
        inventory_type_id: int,
        issue_type_id: int
    ) -> bool:
        stmt = (
            select(
                exists()
                .where(
                    inventory_issue_types.c.inventory_type_id == inventory_type_id,
                    inventory_issue_types.c.issue_type_id == issue_type_id,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar()
