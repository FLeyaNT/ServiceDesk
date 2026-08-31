from __future__ import annotations

from pydantic import BaseModel, Field

from datetime import datetime

from models.tickets import TicketStatus
from models.inventory import InventoryStatus


class TicketCreate(BaseModel):
    description: str
    inventory_id: int
    issue_type_id: int
    is_urgent: bool


class TicketUpdate(BaseModel):
    description: str | None = Field(None)
    inventory_id: int | None = Field(None)
    issue_type_id: int | None = Field(None)
    is_urgent: bool | None = Field(None)
    resolution_note: str | None = Field(None)
    inventory_status: InventoryStatus | None = Field(None)


class TicketResponse(BaseModel):
    id: int
    description: str
    status: TicketStatus
    is_urgent: bool
    creator: UserShortResponse
    assignee: UserShortResponse | None = Field(None)
    inventory: InventoryResponse
    issue_type: IssueTypeResponse
    resolution_note: str | None = Field(None)
    started_at: datetime | None = Field(None)
    completed_at: datetime | None = Field(None)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResolveRequest(BaseModel):
    resolution_note: str | None = Field(None)
    inventory_status: InventoryStatus | None = Field(None)


from .user import UserShortResponse
from .inventory import InventoryResponse
from .issue_types import IssueTypeResponse


TicketResponse.model_rebuild()
