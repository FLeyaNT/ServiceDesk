from __future__ import annotations

from sqlalchemy import (
    String,
    Text
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
    from .tickets import Ticket


class UserRole(str, Enum):
    EMPLOYEE = 'employee'
    TECHNICIAN = 'technician'
    SUPERUSER = 'superuser'

    def __str__(self) -> str:
        return self.value


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        default=UserRole.EMPLOYEE,
        nullable=False
    )

    created_tickets: Mapped[list[Ticket]] = relationship(
        'Ticket',
        foreign_keys='Ticket.created_by',
        back_populates='creator',
        cascade='all, delete-orphan'
    )
    assigned_tickets: Mapped[list[Ticket]] = relationship(
        'Ticket',
        foreign_keys='Ticket.assigned_to',
        back_populates='assignee',
        cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
