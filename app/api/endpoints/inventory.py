from fastapi import (
    APIRouter,
    status,
    Path,
    Depends
)

from typing import Annotated

from core.dependencies import (
    InventoryServiceDep,
    TicketServiceDep,
    require_role
)
from schemas.inventory import InventoryResponse
from schemas.ticket import TicketResponse
from models.users import UserRole
from schemas.session import SessionUser


router = APIRouter(
    prefix='/inventory',
    tags=['Inventory']
)


@router.get(
    '/{inventory_number}',
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK
)
async def get_inventory(
    inventory_number: Annotated[str, Path()],
    inventory_service: InventoryServiceDep
):
    return await inventory_service.get_by_inv_number(
        inventory_number
    )


@router.get(
    '/{inventory_number}/tickets',
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK
)
async def get_inventory_tickets(
    inventory_number: str,
    tickets_service: TicketServiceDep,
    _: SessionUser = Depends(
        require_role(UserRole.TECHNICIAN)
    )
):
    return await (
        tickets_service.get_by_inventory_number(
            inventory_number
        )
    )
