from fastapi import APIRouter
from .models import EventInput
router = APIRouter()

@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}

@router.post("api/v1/events")
async def publish_event(event: EventInput) -> EventInput:
    return event