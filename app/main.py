from fastapi import FastAPI
from app.query_service.routers import router as query_router
from app.core.logging import get_logger

app = FastAPI(title="Query Service")
logger = get_logger("app")

app.include_router(query_router)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Application startup")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Application shutdown")

