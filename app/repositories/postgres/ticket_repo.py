from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from datetime import datetime, timezone

from .base_repo import BaseRepo
from schemas.ticket import TicketCreate, TicketUpdate
from models.tickets import Ticket, TicketStatus


class TicketRepo(BaseRepo[Ticket]):

    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        super().__init__(session, Ticket)

    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        user_id: int
    ) -> Ticket:
        new_ticket = Ticket(
            **ticket_data.model_dump(),
            created_by=user_id
        )

        self.session.add(new_ticket)
        await self.session.commit()
        await self.session.refresh(new_ticket)

        return new_ticket
    
    async def get_all(
        self,
        ticket_status: TicketStatus | None = None
    ) -> list[Ticket]:
        conditions = []

        if ticket_status:
            conditions.append(
                Ticket.status == ticket_status
            )

        return await self.get_many_by_conditions(
            *conditions,
            order_by=Ticket.created_at.desc()
        )
    
    async def get_by_creator(
        self,
        creator_id: int
    ) -> list[Ticket]:
        return await self.get_many_by_conditions(
            Ticket.created_by == creator_id,
            order_by=Ticket.created_at.desc()
        )
    
    async def get_by_assignee(
        self,
        assignee_id: int,
        status: TicketStatus | None
    ) -> list[Ticket]:
        conditions = [
            Ticket.assigned_to == assignee_id
        ]

        if status:
            conditions.append(
                Ticket.status == status
            )
        
        return await self.get_many_by_conditions(
            *conditions,
            order_by=Ticket.started_at.desc()
        )
    
    async def get_by_inventory_id(
        self,
        inventory_id: int
    ) -> list[Ticket]:
        return await self.get_many_by_conditions(
            Ticket.inventory_id == inventory_id,
            order_by=Ticket.created_at.desc()
        )
    
    def valid_to_asignee(
        self,
        ticket: Ticket
    ) -> bool:
        if (
            ticket.assigned_to == None
            and ticket.status == TicketStatus.NEW
        ):
            return True
        return False

    async def set_assignee(
        self,
        ticket: Ticket,
        user_id: int,
    ) -> Ticket: 
        ticket.assigned_to = user_id
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.started_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(ticket)

        return ticket
    
    async def set_resolve(
        self,
        ticket: Ticket,
        resolution_note: str | None
    ) -> Ticket:
        ticket.status = TicketStatus.RESOLVED
        ticket.completed_at = datetime.now(timezone.utc)
        
        if resolution_note:
            ticket.resolution_note = resolution_note

        await self.session.commit()
        await self.session.refresh(ticket)

        return ticket
    
    async def update_ticket(
        self,
        ticket: Ticket,
        update_data: dict[str, Any]
    ) -> Ticket | None:
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket.id)
            .values(**update_data)
            .returning(Ticket)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none()
    