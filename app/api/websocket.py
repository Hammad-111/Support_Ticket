from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

clients: dict[int, list[WebSocket]] = {}


async def notify(ticket_id: int, data: dict):
    for ws in clients.get(ticket_id, []):
        await ws.send_json(data)


@router.websocket("/ws/tickets/{ticket_id}")
async def ticket_ws(websocket: WebSocket, ticket_id: int):
    await websocket.accept()
    clients.setdefault(ticket_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in clients.get(ticket_id, []):
            clients[ticket_id].remove(websocket)
