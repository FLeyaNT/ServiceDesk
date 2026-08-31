from fastapi import (
    APIRouter,
    status,
    Body,
    Path,
    Depends
)

from typing import Annotated

from core.dependencies import (
    CurrentUserDep,
    TicketServiceDep,
    WebSocketManagerDep,
    require_role,
    require_role_or_author,
    get_ticket_service
)
from schemas.ticket import (
    TicketResponse,
    TicketCreate,
    ResolveRequest,
    TicketUpdate
)
from models.users import UserRole
from models.tickets import TicketStatus

from schemas.session import SessionUser


router = APIRouter(
    prefix='/tickets',
    tags=['Tickets']
)


@router.post(
    '/',
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_ticket(
    ticket_data: Annotated[TicketCreate, Body()],
    user: CurrentUserDep,
    ticket_service: TicketServiceDep,
    web_socket_manager: WebSocketManagerDep
):
    ticket = await ticket_service.create_ticket(
        ticket_data,
        user.id
    )

    await (
        web_socket_manager
        .broadcast_new_tickets_count(
            ticket_service
        )
    )

    return ticket


@router.get(
    '/',
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK
)
async def get_tickets(
    ticket_service: TicketServiceDep,
    _: SessionUser = Depends(
        require_role(UserRole.SUPERUSER)
    )
):
    return await ticket_service.get_all()


@router.get(
    '/my',
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK
)
async def get_my_tickets(
    current_user: CurrentUserDep,
    ticket_service: TicketServiceDep
):
    return await ticket_service.get_by_creator(
        current_user.id
    )


@router.get(
    '/assigned',
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK
)
async def get_my_assigned_tickets(
    ticket_service: TicketServiceDep,
    ticket_status: TicketStatus | None = None,
    current_user: SessionUser = Depends(
        require_role(UserRole.TECHNICIAN)
    )
):
    return await ticket_service.get_by_assignee(
        current_user.id,
        ticket_status
    )

@router.get(
    '/new',
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK
)
async def get_new_tickets(
    ticket_service: TicketServiceDep,
    _: SessionUser = Depends(
        require_role(UserRole.TECHNICIAN)
    )
):
    return await ticket_service.get_all(
        ticket_status=TicketStatus.NEW
    )


@router.get(
    '/ticket-statuses',
    response_model=list[TicketStatus],
    status_code=status.HTTP_200_OK
)
def get_ticket_statuses():
    return [status.value for status in TicketStatus]


@router.get(
    '/{resource_id}',
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK
)
async def get_ticket(
    resource_id: Annotated[int, Path()],
    ticket_service: TicketServiceDep,
    _: SessionUser = Depends(
        require_role_or_author(
            get_ticket_service,
            UserRole.TECHNICIAN
        )
    )
):
    return await ticket_service.get_by_id(resource_id)


@router.patch(
    '/{resource_id}',
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK
)
async def update_ticket(
    resource_id: Annotated[int, Path()],
    ticket_service: TicketServiceDep,
    update_data: Annotated[
        TicketUpdate,
        Body()
    ],
    current_user: SessionUser = Depends(
        require_role_or_author(
            get_ticket_service,
            UserRole.TECHNICIAN
        )
    )
):
    return await ticket_service.update_ticket(
        resource_id,
        update_data,
        current_user
    )


@router.patch(
    '/{resource_id}/assign',
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK
)
async def assign_ticket(
    resource_id: Annotated[int, Path()],
    ticket_service: TicketServiceDep,
    web_socket_manager: WebSocketManagerDep,
    current_user: SessionUser = Depends(
        require_role(UserRole.TECHNICIAN)
    )
):
    ticket = await ticket_service.set_assignee(
        resource_id,
        current_user.id
    )

    await (
        web_socket_manager
        .broadcast_new_tickets_count(
            ticket_service
        )
    )

    return ticket


@router.patch(
    '/{resource_id}/resolve',
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK
)
async def resolve_ticket(
    resource_id: Annotated[int, Path()],
    ticket_service: TicketServiceDep,
    resolve_data: Annotated[
        ResolveRequest,
        Body()
    ],
    current_user: SessionUser = Depends(
        require_role(UserRole.TECHNICIAN)
    )
):
    return await ticket_service.resolve_ticket(
        resource_id,
        current_user.id,
        resolve_data
    )
