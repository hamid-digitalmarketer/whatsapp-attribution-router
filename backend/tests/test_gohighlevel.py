"""Tests for GoHighLevel CRM integration adapter."""

from datetime import datetime, timezone

import httpx
import pytest

from app.config import settings
from app.integrations.gohighlevel import GoHighLevelIntegration
from app.schemas import AttributionData, EventRequest, LeadContactData, LeadRequest


@pytest.mark.asyncio
async def test_ghl_anonymous_click_skips_contact_creation():
    adapter = GoHighLevelIntegration()
    settings.ghl_enabled = True
    settings.ghl_api_key = "test_ghl_key"
    settings.ghl_location_id = "loc_123"

    event = EventRequest(
        event_name="whatsapp_click",
        event_id="evt_ghl_anon",
        occurred_at=datetime.now(timezone.utc),
    )

    result = await adapter.dispatch_event(event)
    assert result["status"] == "skipped"
    assert result["reason"] == "anonymous_click_no_pii"

    settings.ghl_enabled = False


@pytest.mark.asyncio
async def test_ghl_lead_upsert_mocked():
    def mock_handler(request: httpx.Request):
        assert "leadconnectorhq.com" in str(request.url)
        assert request.headers.get("Authorization") == "Bearer test_ghl_key"
        return httpx.Response(
            201,
            json={"contact": {"id": "contact_ghl_999", "name": "Client Name"}},
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    adapter = GoHighLevelIntegration(http_client=mock_client)

    settings.ghl_enabled = True
    settings.ghl_api_key = "test_ghl_key"
    settings.ghl_location_id = "loc_123"

    lead = LeadRequest(
        lead_reference="lead_ghl_001",
        contact=LeadContactData(
            first_name="Ahmed",
            last_name="Khan",
            phone="+923167417135",
            email="ahmed@example.com",
        ),
        lead_status="qualified",
        attribution=AttributionData(
            utm_source="meta",
            utm_campaign="spring_promo",
        ),
    )

    result = await adapter.dispatch_lead(lead)
    assert result["status"] == "success"
    assert result["contact_id"] == "contact_ghl_999"
    assert result["action"] == "upserted"

    settings.ghl_enabled = False
