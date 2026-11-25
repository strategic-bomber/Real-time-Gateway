from pydantic import BaseModel, JsonValue


class EventInput(BaseModel):
    room: str
    event_type: str
    payload: JsonValue