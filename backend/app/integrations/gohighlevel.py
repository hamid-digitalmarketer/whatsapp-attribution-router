"""GoHighLevel (GHL) CRM API integration adapter."""

import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings
from app.integrations.base import BaseIntegration
from app.schemas import EventRequest, LeadRequest
from app.services.attribution import normalize_attribution_payload

logger = logging.getLogger(__name__)


class GoHighLevelIntegration(BaseIntegration):
    """Integrates with GoHighLevel LeadConnector v2 API for contact attribution."""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self._client = http_client

    @property
    def name(self) -> str:
        return "gohighlevel"

    @property
    def enabled(self) -> bool:
        return settings.ghl_enabled

    def is_configured(self) -> bool:
        return bool(settings.ghl_api_key and settings.ghl_location_id)

    async def dispatch_event(self, event: EventRequest) -> Dict[str, Any]:
        """Handles anonymous click events.

        Per privacy specifications, does NOT fabricate contacts for anonymous clicks.
        """
        if not self.enabled:
            return {"status": "skipped", "reason": "integration_disabled"}
        if not self.is_configured():
            return {"status": "skipped", "reason": "unconfigured_ghl_credentials"}

        # An anonymous WhatsApp click does not have PII; avoid polluting CRM with ghost contacts
        return {
            "status": "skipped",
            "reason": "anonymous_click_no_pii",
            "message": "Anonymous WhatsApp click recorded; contact creation deferred until lead submission.",
        }

    async def dispatch_lead(self, lead: LeadRequest) -> Dict[str, Any]:
        """Creates or updates a verified contact in GoHighLevel with campaign attribution."""
        if not self.enabled:
            return {"status": "skipped", "reason": "integration_disabled"}
        if not self.is_configured():
            return {"status": "skipped", "reason": "unconfigured_ghl_credentials"}

        contact = lead.contact
        if not contact.email and not contact.phone:
            return {
                "status": "error",
                "detail": "Contact must contain at least a phone number or email address.",
            }

        attr = normalize_attribution_payload(lead.attribution)

        tags = ["WhatsApp Lead", f"Status: {lead.lead_status}"]
        if attr.get("utm_source"):
            tags.append(f"Source: {attr['utm_source']}")
        if attr.get("utm_campaign"):
            tags.append(f"Campaign: {attr['utm_campaign']}")

        payload = {
            "locationId": settings.ghl_location_id,
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "name": f"{contact.first_name or ''} {contact.last_name or ''}".strip() or None,
            "email": contact.email,
            "phone": contact.phone,
            "companyName": contact.company,
            "source": "WhatsApp Attribution Router",
            "tags": tags,
            "customFields": [
                {"id": "lead_reference", "value": lead.lead_reference},
                {"id": "utm_source", "value": attr.get("utm_source") or ""},
                {"id": "utm_medium", "value": attr.get("utm_medium") or ""},
                {"id": "utm_campaign", "value": attr.get("utm_campaign") or ""},
                {"id": "utm_term", "value": attr.get("utm_term") or ""},
                {"id": "utm_content", "value": attr.get("utm_content") or ""},
            ],
        }

        # Filter None values
        payload = {k: v for k, v in payload.items() if v is not None}

        base_url = settings.ghl_api_base_url.rstrip("/")
        url = f"{base_url}/contacts/upsert"

        headers = {
            "Authorization": f"Bearer {settings.ghl_api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
        }

        client = self._client or httpx.AsyncClient(timeout=10.0)
        close_client = self._client is None

        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in {200, 201}:
                data = response.json()
                contact_data = data.get("contact", {})
                return {
                    "status": "success",
                    "contact_id": contact_data.get("id"),
                    "action": "upserted",
                }
            return {
                "status": "error",
                "status_code": response.status_code,
                "detail": response.text,
            }
        except Exception as e:
            logger.error("GoHighLevel API call failed: %s", str(e))
            return {"status": "error", "detail": str(e)}
        finally:
            if close_client:
                await client.aclose()


gohighlevel_integration = GoHighLevelIntegration()
