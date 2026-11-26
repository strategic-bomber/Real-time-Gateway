from pydantic import BaseModel, ConfigDict


class DealFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str | None
    status: str
