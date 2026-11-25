from asyncio import sleep
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

router = APIRouter()


@router.get("/sse", response_class=EventSourceResponse)
async def sse_endpoint() -> AsyncIterator[ServerSentEvent]:
    yield ServerSentEvent(id="1", data={"message": "first"})
    await sleep(1)
    yield ServerSentEvent(id="2", data={"message": "second"})