from fastapi import APIRouter, HTTPException, Request
from .models import EventInput
router = APIRouter()

@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}

@router.post("/api/v1/events")
async def publish_event(request: Request, event: EventInput) -> EventInput:
    room = request.app.state.rooms.get(event.room)
    if room is None:
        raise HTTPException(status_code=400, detail="Unknown room")

    room.publish(event)
    return event