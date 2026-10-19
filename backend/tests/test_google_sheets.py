"""Tests for Google Sheets integration adapter."""

from datetime import datetime, timezone

import httpx
import pytest

from app.config import settings
from app.integrations.google_sheets import SHEETS_COLUMNS, GoogleSheetsIntegration
from app.schemas import AttributionData, DestinationData, EventRequest, PageData


@pytest.mark.asyncio
async def test_google_sheets_event_row_building():
    adapter = GoogleSheetsIntegration()
    event = EventRequest(
        event_name="whatsapp_click",
        event_id="evt_gsheet_001",
        occurred_at=datetime(2026, 10, 19, 10, 30, tzinfo=timezone.utc),
        lead_reference="lead_ref_123",
        attribution=AttributionData(
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="summer_leads",
        ),
        page=PageData(landing_page="https://example.com/demo"),
        destination=DestinationData(
            type="whatsapp",
            phone_number="923167417135",
            button_id="primary_cta",
        ),
    )

    row = adapter._build_event_row(event)
    assert len(row) == len(SHEETS_COLUMNS)
    assert row[1] == "evt_gsheet_001"
    assert row[2] == "whatsapp_click"
    assert row[3] == "lead_ref_123"
    assert row[4] == "google"
    assert row[5] == "cpc"
    assert row[6] == "summer_leads"
    assert row[11] == "primary_cta"
    assert row[12] == "923167417135"


@pytest.mark.asyncio
async def test_google_sheets_dispatch_mocked():
    # Setup mock httpx handler
    def mock_handler(request: httpx.Request):
        assert "sheets.googleapis.com" in str(request.url)
        return httpx.Response(
            200,
            json={"updates": {"updatedRows": 1, "updatedColumns": 14}},
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    adapter = GoogleSheetsIntegration(http_client=mock_client)

    settings.google_sheets_enabled = True
    settings.google_sheets_spreadsheet_id = "test_sheet_id_123"

    event = EventRequest(
        event_name="whatsapp_click",
        event_id="evt_gsheet_002",
        occurred_at=datetime.now(timezone.utc),
        lead_reference="lead_456",
    )

    result = await adapter.dispatch_event(event)
    assert result["status"] == "success"
    assert result["spreadsheet_id"] == "test_sheet_id_123"
    assert result["updated_rows"] == 1

    settings.google_sheets_enabled = False
    settings.google_sheets_spreadsheet_id = ""
