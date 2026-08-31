from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from typing import TYPE_CHECKING

from .base_model import Base
from .inventory_issue_types import inventory_issue_types

if TYPE_CHECKING:
    from .inventory_types import InventoryType
    from .tickets import Ticket


class IssueType(Base):
    __tablename__ = 'issue_types'

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    inventory_types: Mapped[list[InventoryType]] = relationship(
        'InventoryType',
        secondary=inventory_issue_types,
        back_populates='issue_types'
    )
    tickets: Mapped[list[Ticket]] = relationship(
        'Ticket',
        back_populates='issue_type',
        cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"<IssueType(id={self.id}, name='{self.name}')>"
