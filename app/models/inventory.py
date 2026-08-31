from __future__ import annotations

from sqlalchemy import (
    String,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from typing import TYPE_CHECKING
from enum import Enum

from .base_model import Base

if TYPE_CHECKING:
    from .inventory_types import InventoryType
    from .tickets import Ticket


class InventoryStatus(str, Enum):
    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    BROKEN = 'broken'
    WRITTEN_OFF = 'written_off'

    def __str__(self) -> str:
        return self.value


class Inventory(Base):
    __tablename__ = 'inventory'

    inventory_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    type_id: Mapped[int] = mapped_column(
        ForeignKey('inventory_types.id', ondelete='CASCADE'),
        nullable=False
    )
    status: Mapped[InventoryStatus] = mapped_column(
        default=InventoryStatus.ASSIGNED,
        nullable=False
    )
    location: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    type: Mapped[InventoryType] = relationship(
        'InventoryType',
        back_populates='inventories'
    )
    tickets: Mapped[list[Ticket]] = relationship(
        'Ticket',
        back_populates='inventory',
        cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"<Inventory(id={self.id}, number='{self.inventory_number}', status='{self.status}')>"
