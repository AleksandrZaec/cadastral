from fastapi import APIRouter, Depends, Query, status
from typing import List, Dict
from app.query_service.schemas import RequestCreate, RequestRead
from app.query_service.dependencies import get_request_service
from app.core.logging import get_logger
from app.query_service.services import RequestService

router = APIRouter()
logger = get_logger("api")


@router.get("/ping", summary="Health check", description="Returns simple ok status.")
async def ping() -> Dict[str, str]:
    """Health check endpoint."""
    logger.debug("Ping requested")
    return {"status": "ok"}


@router.post(
    "/query",
    response_model=RequestRead,
    summary="Create and process a cadastral query",
    description="Persists incoming request, calls external service, stores result, and returns it.",
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def query_endpoint(
        request: RequestCreate,
        service: RequestService = Depends(get_request_service)
) -> RequestRead:
    """Create a `Request` and delegate processing to the service layer."""
    logger.info("Incoming query", extra={"cadastral_number": request.cadastral_number})
    result = await service.process_request(
        cadastral_number=request.cadastral_number,
        latitude=request.latitude,
        longitude=request.longitude
    )
    logger.info("Query processed", extra={"request_id": result.id, "success": result.success})
    return result


@router.get(
    "/history",
    response_model=List[RequestRead],
    summary="List history",
    description="Returns all requests ordered by creation time desc with pagination.",
    response_model_exclude_none=True,
)
async def history(
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        service: RequestService = Depends(get_request_service)
) -> List[RequestRead]:
    """Return the entire query history with pagination."""
    logger.debug("History requested", extra={"limit": limit, "offset": offset})
    items = await service.get_history_all(limit=limit, offset=offset)
    logger.info("History returned", extra={"count": len(items)})
    return items


@router.get(
    "/history/{cadastral_number}",
    response_model=List[RequestRead],
    summary="List history by cadastral number",
    description="Returns requests filtered by cadastral number ordered by creation time desc with pagination.",
    response_model_exclude_none=True,
)
async def history_by_cadastral(
        cadastral_number: str,
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        service: RequestService = Depends(get_request_service)
) -> List[RequestRead]:
    """Return request history for a specific cadastral number with pagination."""
    logger.debug("History by cadastral requested", extra={"cadastral_number": cadastral_number, "limit": limit, "offset": offset})
    items = await service.get_history_by_cadastral_number(cadastral_number, limit=limit, offset=offset)
    logger.info("History by cadastral returned", extra={"cadastral_number": cadastral_number, "count": len(items)})
    return items
