from pydantic import BaseModel, JsonValue

from typing import Literal

class EventInput(BaseModel):
    room: str
    event_type: str
    payload: JsonValue




class RoomCommand(BaseModel):
    action: Literal["subscribe", "unsubscribe"]
    room: str