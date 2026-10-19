"""Operational status endpoint for configured integrations."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import IntegrationsStatusResponse, IntegrationStatusItem
from app.security import mask_secret

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


@router.get(
    "/status",
    response_model=IntegrationsStatusResponse,
    summary="Get operational status of configured integrations",
)
async def get_integrations_status():
    """Returns safe operational status of configured integrations without leaking secrets."""
    sheets_configured = bool(settings.google_sheets_spreadsheet_id.strip())
    sheets_status = (
        "ready"
        if (settings.google_sheets_enabled and sheets_configured)
        else ("disabled" if not settings.google_sheets_enabled else "unconfigured")
    )

    ghl_configured = bool(settings.ghl_api_key and settings.ghl_location_id)
    ghl_status = (
        "ready"
        if (settings.ghl_enabled and ghl_configured)
        else ("disabled" if not settings.ghl_enabled else "unconfigured")
    )

    webhook_configured = bool(
        settings.outbound_webhook_url and settings.outbound_webhook_url.startswith("http")
    )
    webhook_status = (
        "ready"
        if (settings.outbound_webhook_enabled and webhook_configured)
        else ("disabled" if not settings.outbound_webhook_enabled else "unconfigured")
    )

    return IntegrationsStatusResponse(
        google_sheets=IntegrationStatusItem(
            enabled=settings.google_sheets_enabled,
            configured=sheets_configured,
            status=sheets_status,
            details={
                "spreadsheet_id": mask_secret(settings.google_sheets_spreadsheet_id),
                "worksheet_name": settings.google_sheets_worksheet_name,
            },
        ),
        gohighlevel=IntegrationStatusItem(
            enabled=settings.ghl_enabled,
            configured=ghl_configured,
            status=ghl_status,
            details={
                "location_id": mask_secret(settings.ghl_location_id),
                "api_base_url": settings.ghl_api_base_url,
            },
        ),
        outbound_webhook=IntegrationStatusItem(
            enabled=settings.outbound_webhook_enabled,
            configured=webhook_configured,
            status=webhook_status,
            details={
                "webhook_url": (
                    settings.outbound_webhook_url[:25] + "..."
                    if settings.outbound_webhook_url
                    else ""
                ),
                "has_hmac_secret": bool(settings.outbound_webhook_secret),
                "max_retries": settings.outbound_webhook_max_retries,
            },
        ),
    )
