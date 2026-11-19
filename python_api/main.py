from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from python_api.db import init_db
from routers import auth, deals, fields, messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняемый при запуске
    init_db()
    yield
    # Код, выполняемый при завершении (если нужен)

app = FastAPI(title="Deal API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(deals.router)
app.include_router(fields.router)
app.include_router(messages.router)