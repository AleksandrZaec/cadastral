import httpx
from typing import Dict, Any
from app.core.config import settings
from app.core.logging import get_logger


class ExternalServiceError(Exception):
    """Exception for external service errors."""
    pass


logger = get_logger("external")


async def send_to_external_service(payload: Dict[str, Any], timeout: int = 60) -> bool:
    """Send JSON payload to external service and return success flag."""
    external_url = settings.EXTERNAL_SERVICE_URL
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(external_url, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("External request succeeded", extra={"payload": payload, "status_code": response.status_code})
    except httpx.TimeoutException:
        logger.error("External request timeout", extra={"payload": payload})
        raise ExternalServiceError("timeout")
    except httpx.HTTPError as e:
        logger.error("External HTTP error", extra={"payload": payload, "error": str(e)})
        raise ExternalServiceError(f"http_error: {e}")
    except Exception as e:
        logger.exception("External unexpected error")
        raise ExternalServiceError(f"unexpected_error: {e}")

    success = data.get("success")
    if isinstance(success, bool):
        return success
    else:
        logger.error("External invalid response", extra={"response": data})
        raise ExternalServiceError("invalid_response")
