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
    from .inventory import Inventory
    from .issue_types import IssueType


class InventoryType(Base):
    __tablename__ = 'inventory_types'

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    inventories: Mapped[list[Inventory]] = relationship(
        'Inventory',
        back_populates='type',
        cascade='all, delete-orphan'
    )
    issue_types: Mapped[list[IssueType]] = relationship(
        'IssueType',
        secondary=inventory_issue_types,
        back_populates='inventory_types',
    )

    def __repr__(self) -> str:
        return f"<InventoryType(id={self.id}, name='{self.name}')>"
