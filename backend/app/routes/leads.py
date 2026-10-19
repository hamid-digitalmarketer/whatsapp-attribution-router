"""Protected server-to-server lead records ingestion route."""

from fastapi import APIRouter, Depends, status

from app.schemas import LeadRequest, LeadResponse
from app.security import verify_api_key
from app.services.event_processor import event_processor

router = APIRouter(prefix="/api/v1", tags=["Leads"])


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
    summary="Submit or update verified lead record",
)
async def ingest_lead(lead: LeadRequest):
    """Protected endpoint for submitting qualified leads from webhooks, forms, or CRM syncs.

    Requires administrative API key authentication (X-API-Key or Bearer token).
    Forwards contact details and attribution tags to GoHighLevel, Google Sheets, or webhooks.
    """
    response = await event_processor.process_lead(lead)
    return response
