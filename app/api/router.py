from fastapi import APIRouter

from api.endpoints import auth
from api.endpoints import inventory_types
from api.endpoints import inventory
from api.endpoints import tickets
from api.endpoints import ws


api_router = APIRouter()


api_router.include_router(
    auth.router
)

api_router.include_router(
    inventory.router
)

api_router.include_router(
    inventory_types.router
)

api_router.include_router(
    tickets.router
)

api_router.include_router(
    ws.router
)
