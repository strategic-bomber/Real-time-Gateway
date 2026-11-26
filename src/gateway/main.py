from fastapi import FastAPI

from . import api, ws, sse
from .rooms import Room

app = FastAPI()

app.state.rooms = {"1042": Room()}

app.include_router(api.router)
app.include_router(ws.router)
app.include_router(sse.router)
