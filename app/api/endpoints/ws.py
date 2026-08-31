from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from core.dependencies import (
    WebSocketManagerDep,
    TicketServiceDep
)


router = APIRouter(
    prefix='/ws'
)


@router.websocket(
    '/new-tickets'
)
async def websocket_new_tickets(
    websocket: WebSocket,
    web_socket_manager: WebSocketManagerDep,
    ticket_service: TicketServiceDep
):
    await web_socket_manager.connect(websocket)

    await web_socket_manager.broadcast_new_tickets_count(
        ticket_service
    )

    await ticket_service.session.close()

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        web_socket_manager.disconnect(websocket)
