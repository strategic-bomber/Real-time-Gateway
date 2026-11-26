from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
from .rooms import Room, EventQueue
from .models import RoomCommand
from pydantic import ValidationError

import asyncio

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()

    rooms: dict[str, Room] = socket.app.state.rooms
    queue: EventQueue = asyncio.Queue(maxsize=128)
    subscriptions: set[Room] = set()

    async def receive_commands() -> None:
        while True:
            raw = await socket.receive_text()
            try:
                command = RoomCommand.model_validate_json(raw)
            except ValidationError as exc:
                raise WebSocketException(code=1008, reason="Invalid command") from exc

            room = rooms.get(command.room)
            if room is None:
                raise WebSocketException(code=1008, reason="Unknown room")

            if command.action == "subscribe":
                room.subscribe(queue)
                subscriptions.add(room)
            else:
                room.unsubscribe(queue)
                subscriptions.discard(room)

    async def send_events() -> None:
        while True:
            event = await queue.get()
            await socket.send_json(event.model_dump(mode="json"))

    tasks = (
        asyncio.create_task(receive_commands()),
        asyncio.create_task(send_events()),
    )
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    except WebSocketDisconnect:
        pass
    finally:
        for task in tasks:
            task.cancel()
        for room in subscriptions:
            room.unsubscribe(queue)
        await asyncio.gather(*tasks, return_exceptions=True)