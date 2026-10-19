"""Public browser attribution events ingestion route."""

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas import EventRequest, EventResponse
from app.security import rate_limiter
from app.services.event_processor import event_processor

router = APIRouter(prefix="/api/v1", tags=["Events"])


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest browser attribution event",
)
async def ingest_event(event: EventRequest, request: Request):
    """Public ingestion endpoint for browser attribution events (e.g. whatsapp_click).

    Validates payload, enforces client IP rate limits, performs deduplication, and
    forwards events to configured integrations.
    """
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before submitting additional events.",
        )

    response = await event_processor.process_event(event)
    return response
