from pydantic import BaseModel

from models.inventory import InventoryStatus


class InventoryResponse(BaseModel):
    id: int
    inventory_number: str
    type_id: int
    status: InventoryStatus
    location: str

    class Config:
        from_attributes = True
