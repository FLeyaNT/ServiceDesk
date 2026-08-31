from repositories.postgres import InventoryRepo
from core import exceptions
from schemas.inventory import InventoryResponse
from models.inventory import (
    Inventory,
    InventoryStatus
)


class InventoryService:
    inventory_repo: InventoryRepo

    def __init__(
        self,
        inventory_repo: InventoryRepo
    ) -> None:
        self.inventory_repo = inventory_repo

    async def get_by_id(
        self,
        inventory_id: int
    ) -> InventoryResponse:
        inventory = await (
            self.inventory_repo.get_by_id(
                inventory_id
            )
        )

        if not inventory:
            raise exceptions.NotFoundException(
                'Inventory not found'
            )
        
        return inventory

    async def get_by_inv_number(
        self,
        inv_number: str
    ) -> InventoryResponse:
        
        inventory = await (
            self.inventory_repo
            .get_by_inv_number(inv_number)
        )

        if not inventory:
            raise exceptions.NotFoundException(
                'Inventory not found'
            )
        
        return InventoryResponse.model_validate(inventory)
    
    async def update_status(
        self,
        inventory: Inventory,
        status: InventoryStatus
    ) -> Inventory:
        return await self.inventory_repo.update_status(
            inventory,
            status
        )
