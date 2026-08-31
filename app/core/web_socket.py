from fastapi import (
    WebSocket
)

from services import TicketService
from models.tickets import TicketStatus


class WebSocketManager:
    active_connections: list[WebSocket]

    def __init__(
        self,
    ) -> None:
        self.active_connections = []

    async def connect(
        self,
        websocket: WebSocket
    ) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(
        self,
        websocket: WebSocket
    ) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_new_tickets_count(
        self,
        ticket_service: TicketService
    ) -> None:
        new_tickets = await ticket_service.get_all(
            ticket_status=TicketStatus.NEW
        )

        for connection in self.active_connections:
            try:
                await connection.send_json({
                    "event": "new_tickets_count",
                    "count": len(new_tickets)
                })
            except:
                pass
