"""Tests for generic outbound webhook adapter."""

import hashlib
import hmac
import json
from datetime import datetime, timezone

import httpx
import pytest

from app.config import settings
from app.integrations.webhook import WebhookIntegration
from app.schemas import EventRequest


@pytest.mark.asyncio
async def test_webhook_dispatch_and_signature():
    captured_request = {}

    def mock_handler(request: httpx.Request):
        captured_request["url"] = str(request.url)
        captured_request["body"] = request.read()
        captured_request["headers"] = dict(request.headers)
        return httpx.Response(200, json={"received": True})

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    adapter = WebhookIntegration(http_client=mock_client)

    settings.outbound_webhook_enabled = True
    settings.outbound_webhook_url = "https://agency-crm.example.com/webhook"
    settings.outbound_webhook_secret = "secret_signing_key_456"

    event = EventRequest(
        event_name="whatsapp_click",
        event_id="evt_webhook_001",
        occurred_at=datetime.now(timezone.utc),
        lead_reference="lead_wh_123",
    )

    result = await adapter.dispatch_event(event)
    assert result["status"] == "success"
    assert captured_request["url"] == "https://agency-crm.example.com/webhook"

    # Verify signature
    signature = captured_request["headers"].get("x-war-signature")
    assert signature is not None
    expected_sig = hmac.new(
        b"secret_signing_key_456",
        captured_request["body"],
        hashlib.sha256,
    ).hexdigest()
    assert signature == expected_sig

    # Verify payload format
    payload = json.loads(captured_request["body"].decode("utf-8"))
    assert payload["type"] == "event"
    assert payload["data"]["event_id"] == "evt_webhook_001"

    settings.outbound_webhook_enabled = False
    settings.outbound_webhook_url = None
    settings.outbound_webhook_secret = None
