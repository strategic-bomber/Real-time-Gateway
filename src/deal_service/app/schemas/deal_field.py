from pydantic import BaseModel, ConfigDict
from typing import Literal


class DealFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str | None
    status: str

class DealFieldUpdate(BaseModel):
    value: str

class DealFieldStatusUpdate(BaseModel):
    status: Literal["approved", "changes_requested"]
