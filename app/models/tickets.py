from __future__ import annotations

from sqlalchemy import (
    ForeignKey,
    Text,
    DateTime
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from typing import TYPE_CHECKING
from enum import Enum
from datetime import datetime

from .base_model import Base

if TYPE_CHECKING:
    from .users import User
    from .inventory import Inventory
    from .issue_types import IssueType


class TicketStatus(str, Enum):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'


class Ticket(Base):
    __tablename__ = 'tickets'

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    status: Mapped[TicketStatus] = mapped_column(
        default=TicketStatus.NEW,
        nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True
    )
    inventory_id: Mapped[int] = mapped_column(
        ForeignKey('inventory.id', ondelete='CASCADE'),
        nullable=False
    )
    issue_type_id: Mapped[int] = mapped_column(
        ForeignKey('issue_types.id', ondelete='CASCADE'),
        nullable=False
    )
    is_urgent: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )
    resolution_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    creator: Mapped[User] = relationship(
        'User',
        foreign_keys=(created_by,),
        back_populates='created_tickets',
        lazy='joined'
    )
    assignee: Mapped[User | None] = relationship(
        'User',
        foreign_keys=(assigned_to),
        back_populates='assigned_tickets',
        lazy='joined'
    )
    inventory: Mapped[Inventory] = relationship(
        'Inventory',
        back_populates='tickets',
        lazy='joined'
    )
    issue_type: Mapped[IssueType] = relationship(
        'IssueType',
        back_populates='tickets',
        lazy='joined'
    )

    def __repr__(self) -> str:
        return f"<Ticket(id={self.id}, status='{self.status}', created_by={self.created_by})>"
