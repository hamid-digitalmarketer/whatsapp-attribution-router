"""Google Sheets API v4 integration adapter."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.integrations.base import BaseIntegration
from app.schemas import EventRequest, LeadRequest
from app.services.attribution import normalize_attribution_payload

logger = logging.getLogger(__name__)

# Standard columns schema
SHEETS_COLUMNS = [
    "timestamp",
    "event_id",
    "event_name",
    "lead_reference",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "landing_page",
    "referrer",
    "whatsapp_button_id",
    "destination_phone",
    "lead_status",
]


class GoogleSheetsIntegration(BaseIntegration):
    """Appends attributed events and CRM lead updates to Google Sheets."""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self._client = http_client

    @property
    def name(self) -> str:
        return "google_sheets"

    @property
    def enabled(self) -> bool:
        return settings.google_sheets_enabled

    def is_configured(self) -> bool:
        return bool(settings.google_sheets_spreadsheet_id.strip())

    def _build_event_row(self, event: EventRequest) -> List[Any]:
        attr = normalize_attribution_payload(event.attribution)
        page = event.page or None
        dest = event.destination or None

        return [
            event.occurred_at.isoformat(),
            event.event_id,
            event.event_name,
            event.lead_reference or "",
            attr.get("utm_source") or "",
            attr.get("utm_medium") or "",
            attr.get("utm_campaign") or "",
            attr.get("utm_content") or "",
            attr.get("utm_term") or "",
            page.landing_page if page else "",
            page.referrer if page else "",
            dest.button_id if dest else "",
            dest.phone_number if dest else "",
            "unconfirmed_click",
        ]

    def _build_lead_row(self, lead: LeadRequest) -> List[Any]:
        attr = normalize_attribution_payload(lead.attribution)
        contact_str = f"{lead.contact.first_name or ''} {lead.contact.last_name or ''}".strip()
        if lead.contact.phone:
            contact_str += f" ({lead.contact.phone})"

        return [
            "",  # timestamp filled by sheets or current time
            "",  # event_id
            "lead_status_updated",
            lead.lead_reference,
            attr.get("utm_source") or "",
            attr.get("utm_medium") or "",
            attr.get("utm_campaign") or "",
            attr.get("utm_content") or "",
            attr.get("utm_term") or "",
            "",
            contact_str,
            "crm_lead",
            lead.contact.phone or "",
            lead.lead_status,
        ]

    async def _append_values(self, values: List[List[Any]]) -> Dict[str, Any]:
        spreadsheet_id = settings.google_sheets_spreadsheet_id
        worksheet = settings.google_sheets_worksheet_name or "Attribution Leads"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{worksheet}!A:N:append"

        params = {"valueInputOption": "USER_ENTERED"}
        payload = {"values": values}

        headers = {"Content-Type": "application/json"}
        # In production with OAuth/ADC, Authorization header is attached
        if settings.google_service_account_json:
            headers["Authorization"] = "Bearer simulated_gcp_token"

        client = self._client or httpx.AsyncClient(timeout=10.0)
        close_client = self._client is None

        try:
            response = await client.post(url, params=params, json=payload, headers=headers)
            if response.status_code in {200, 201}:
                data = response.json()
                return {
                    "status": "success",
                    "spreadsheet_id": spreadsheet_id,
                    "updated_rows": data.get("updates", {}).get("updatedRows", 1),
                }
            return {
                "status": "error",
                "status_code": response.status_code,
                "detail": response.text,
            }
        except Exception as e:
            logger.error("Google Sheets API request failed: %s", str(e))
            return {"status": "error", "detail": str(e)}
        finally:
            if close_client:
                await client.aclose()

    async def dispatch_event(self, event: EventRequest) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "skipped", "reason": "integration_disabled"}
        if not self.is_configured():
            return {"status": "skipped", "reason": "unconfigured_spreadsheet_id"}

        row = self._build_event_row(event)
        return await self._append_values([row])

    async def dispatch_lead(self, lead: LeadRequest) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "skipped", "reason": "integration_disabled"}
        if not self.is_configured():
            return {"status": "skipped", "reason": "unconfigured_spreadsheet_id"}

        row = self._build_lead_row(lead)
        return await self._append_values([row])


google_sheets_integration = GoogleSheetsIntegration()
