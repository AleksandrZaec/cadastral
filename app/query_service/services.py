from typing import List, Optional
from app.query_service.models import Request
from app.query_service.repositories import AbstractRequestRepository
from app.query_service.utils import send_to_external_service, ExternalServiceError
from fastapi import HTTPException
from app.core.logging import get_logger


class RequestService:
    """Orchestrates request processing and history retrieval."""

    def __init__(self, repository: AbstractRequestRepository):
        self.repository: AbstractRequestRepository = repository
        self.logger = get_logger("service")

    async def process_request(self, cadastral_number: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Request:
        """Create a `Request`, call external service, persist result, and return entity."""
        payload = {"cadastral_number": cadastral_number, "latitude": latitude, "longitude": longitude}

        request = Request(cadastral_number=cadastral_number, latitude=latitude, longitude=longitude, payload=payload)
        request = await self.repository.create(request)

        try:
            success = await send_to_external_service(payload)
            request = await self.repository.update_request_result(request=request, response={"success": success}, success=success)
            self.logger.info("Processed request successfully", extra={"request_id": request.id, "success": success})
            return request

        except ExternalServiceError as e:
            request = await self.repository.update_request_result(request=request, response={"success": None, "error": str(e)}, success=None)
            error_text = str(e)
            self.logger.error("Processing failed", extra={"request_id": request.id, "error": error_text})

            if error_text == "timeout":
                raise HTTPException(status_code=504, detail={"message": "External service timeout (more than 60 sec)", "request_id": request.id})
            elif error_text.startswith("http_error") or error_text == "invalid_response":
                raise HTTPException(status_code=502, detail={"message": f"External service error: {error_text}", "request_id": request.id})
            else:
                raise HTTPException(status_code=500, detail={"message": f"External service error: {error_text}", "request_id": request.id})

    async def get_history_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Request]:
        """Return all requests with pagination."""
        return await self.repository.get_all(limit=limit, offset=offset)

    async def get_history_by_cadastral_number(self, cadastral_number: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Request]:
        """Return requests filtered by cadastral number with pagination."""
        return await self.repository.get_by_cadastral_number(cadastral_number, limit=limit, offset=offset)
