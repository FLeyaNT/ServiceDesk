from sqlalchemy.ext.asyncio import AsyncSession

from .base_repo import BaseRepo
from models.inventory import (
    Inventory,
    InventoryStatus
)


class InventoryRepo(BaseRepo[Inventory]):

    def __init__(
        self,
        session: AsyncSession
    ):
        super().__init__(session, Inventory)

    async def get_by_inv_number(
        self,
        inv_number: str
    ) -> Inventory | None:
        return await self.get_one_by_conditions(
            Inventory.inventory_number == inv_number
        )
    
    async def update_status(
        self,
        inventory: Inventory,
        status: InventoryStatus
    ) -> Inventory:
        inventory.status = status

        await self.session.commit()
        await self.session.refresh(inventory)

        return inventory
