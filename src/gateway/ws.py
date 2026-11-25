from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()

    try:
        while True:
            message = await socket.receive_text()
            await socket.send_text(message)
    except WebSocketDisconnect:
        return