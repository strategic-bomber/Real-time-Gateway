from fastapi import FastAPI

from . import api, ws, sse

app = FastAPI()



app.include_router(api.router)
app.include_router(ws.router)
app.include_router(sse.router)
