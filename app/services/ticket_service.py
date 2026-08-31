from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.session import SessionUser
from repositories.postgres import (
    IssueTypesRepo,
    TicketRepo
)
from core import exceptions
from schemas.ticket import (
    TicketCreate,
    TicketResponse,
    ResolveRequest,
    TicketUpdate
)
from models import Ticket
from models.tickets import TicketStatus
from .inventory_service import InventoryService
from models.users import UserRole


class TicketService:
    ticket_repo: TicketRepo
    inventory_service: InventoryService
    issue_types_repo: IssueTypesRepo
    session: AsyncSession

    def __init__(
        self,
        ticket_repo: TicketRepo,
        inventory_service: InventoryService,
        issue_types_repo: IssueTypesRepo
    ) -> None:
        self.ticket_repo = ticket_repo
        self.inventory_service = inventory_service
        self.issue_types_repo = issue_types_repo
        self.session = self.ticket_repo.session
        
    async def _check_issue_type(
        self,
        issue_type_id: int
    ) -> None:
        issue_type_exists = await (
            self.issue_types_repo.get_by_id(
                issue_type_id
            )
        )
        if not issue_type_exists:
            raise exceptions.NotFoundException(
                'Issue type not found'
            )
        
    async def _check_compatibility(
        self,
        inventory_type_id: int,
        issue_type_id: int
    ) -> None:
        is_compatible = await (
            self.issue_types_repo.check_compatibility(
                inventory_type_id,
                issue_type_id
            )
        )
        if not is_compatible:
            raise exceptions.ConflictException(
                'Inventory type and issue type is uncompatible'
            )
        
    def _get_pydantic_list(
        self,
        tickets: Ticket
    ) -> list[TicketResponse]:
        pydantic_list = []
        
        for ticket in tickets:
            pydantic_list.append(
                TicketResponse.model_validate(ticket)
            )
        
        return pydantic_list
    
    async def close_session(
        self
    ) -> None:
        await self.session.close()
    
    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        user_id: int
    ) -> TicketResponse:
        inventory = await self.inventory_service.get_by_id(
            ticket_data.inventory_id
        )

        await self._check_issue_type(
            ticket_data.issue_type_id
        )

        await self._check_compatibility(
            inventory.type_id,
            ticket_data.issue_type_id
        )
        
        ticket = await self.ticket_repo.create_ticket(
            ticket_data,
            user_id
        )

        return TicketResponse.model_validate(ticket)
    
    async def get_by_id(
        self,
        ticket_id: int,
        raw_model: bool = False
    ) -> TicketResponse | Ticket:
        ticket = await self.ticket_repo.get_by_id(
            ticket_id
        )
        if not ticket:
            raise exceptions.NotFoundException(
                'Ticket not found'
            )
        
        if raw_model:
            return ticket
        
        return TicketResponse.model_validate(ticket)
    
    async def set_assignee(
        self,
        ticket_id: int,
        user_id: int
    ) -> TicketResponse:
        ticket = await self.get_by_id(ticket_id, raw_model=True)

        is_valid = self.ticket_repo.valid_to_asignee(ticket)
        if not is_valid:
            raise exceptions.ConflictException(
                'Ticket is already assigned'
            )
        
        print(f'USER_ID: {user_id}')

        updated_ticket = await self.ticket_repo.set_assignee(
            ticket,
            user_id
        )
        
        return TicketResponse.model_validate(updated_ticket)
    
    def valid_to_resolve(
        self,
        ticket: Ticket,
        user_id: int
    ) -> None:
        if ticket.assigned_to != user_id:
            raise exceptions.ForbiddenException()
        
        if ticket.status != TicketStatus.IN_PROGRESS:
            raise exceptions.ConflictException(
                'Ticket allready resolved'
            )

    async def resolve_ticket(
        self,
        ticket_id: int,
        user_id: int,
        resolve_request: ResolveRequest
    ) -> TicketResponse:
        ticket = await self.get_by_id(ticket_id, raw_model=True)

        self.valid_to_resolve(ticket, user_id)

        updated_ticket = await self.ticket_repo.set_resolve(
            ticket,
            resolve_request.resolution_note
        )

        if resolve_request.inventory_status:
            await self.inventory_service.update_status(
                ticket.inventory,
                resolve_request.inventory_status
            )

        return updated_ticket
    
    async def get_by_creator(
        self,
        creator_id: int
    ) -> list[TicketResponse]:
        tickets = await self.ticket_repo.get_by_creator(
            creator_id
        )
        return self._get_pydantic_list(tickets)
    
    async def get_by_assignee(
        self,
        assignee_id: int,
        ticket_status: TicketStatus | None
    ):
        tickets = await self.ticket_repo.get_by_assignee(
            assignee_id,
            ticket_status
        )
        return self._get_pydantic_list(tickets)
    
    async def get_by_inventory_number(
        self,
        inventory_number: str
    ) -> list[TicketResponse]:
        
        inventory = await (
            self.inventory_service
            .get_by_inv_number(inventory_number)
        )

        tickets = await (
            self.ticket_repo
            .get_by_inventory_id(inventory.id)
        )

        return self._get_pydantic_list(tickets)
    
    async def get_all(
        self,
        ticket_status: TicketStatus | None = None
    ) -> list[TicketResponse]:
        tickets = await self.ticket_repo.get_all(
            ticket_status
        )
        return self._get_pydantic_list(tickets)
    
    async def update_ticket(
        self,
        ticket_id: int,
        update_data: TicketUpdate,
        user: SessionUser
    ) -> TicketResponse:
        ticket = await self.get_by_id(ticket_id, raw_model=True)

        update_data: dict[str, Any] = update_data.model_dump(exclude_unset=True)

        if user.id == ticket.created_by:
            if ticket.status != TicketStatus.NEW:
                raise exceptions.ConflictException(
                    'Only new tickets can be updated'
                )
            update_data.pop('resolution_note', None)
            update_data.pop('inventory_status', None)
            self._check_compatibility(
                update_data.get('inventory_id', ticket.inventory_id),
                update_data.get('issue_type_id', ticket.issue_type_id)
            )
        elif user.role == UserRole.TECHNICIAN:
            if ticket.assigned_to != user.id:
                raise exceptions.ForbiddenException()
            if ticket.status != TicketStatus.RESOLVED:
                raise exceptions.ConflictException(
                    'Only tickets resolved can be updated'
                )
            update_data.pop('inventory_id', None)
            update_data.pop('issue_type_id', None)
            update_data.pop('description', None)
            update_data.pop('is_urgent', None)

        updated_ticket = await self.ticket_repo.update_ticket(
            ticket,
            update_data
        )

        return TicketResponse.model_validate(updated_ticket)
