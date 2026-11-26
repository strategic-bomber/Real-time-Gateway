from fastapi import FastAPI

from app.database import Base, engine
from app import models

from app.routers.deals import router as deals_router

app = FastAPI(
    title="Deal Service",
    description="API for vehicle buyout deals",
    version="0.1.0",
)
app.include_router(deals_router)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}
