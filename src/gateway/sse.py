from asyncio import Queue
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.sse import EventSourceResponse, ServerSentEvent

from .rooms import EventQueue

router = APIRouter()


async def subscribe_to_room(
    request: Request, room: str
) -> AsyncIterator[EventQueue]:
    current_room = request.app.state.rooms.get(room)
    if current_room is None:
        raise HTTPException(status_code=404, detail="Unknown room")

    queue: EventQueue = Queue(maxsize=128)
    current_room.subscribe(queue)
    try:
        yield queue
    finally:
        current_room.unsubscribe(queue)


@router.get("/sse", response_class=EventSourceResponse)
async def sse_endpoint(
    queue: Annotated[EventQueue, Depends(subscribe_to_room)],
) -> AsyncIterator[ServerSentEvent]:
    while True:
        event = await queue.get()
        yield ServerSentEvent(data=event.model_dump(mode="json"))