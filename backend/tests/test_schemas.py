"""Tests for schemas, normalization, and channel classification."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import AttributionData, EventRequest, LeadContactData, LeadRequest
from app.services.attribution import classify_channel_group


def test_channel_grouping_classification():
    assert classify_channel_group("google", "cpc") == "Paid Search"
    assert classify_channel_group("facebook", "paid_social") == "Paid Social"
    assert classify_channel_group("meta", "cpc") == "Paid Social"
    assert classify_channel_group("google", "organic") == "Organic Search"
    assert classify_channel_group("newsletter", "email") == "Email"
    assert classify_channel_group("partner_blog", "referral") == "Referral / Affiliate"
    assert classify_channel_group(None, None) == "Direct / Unattributed"


def test_attribution_data_sanitization():
    attr = AttributionData(
        utm_source=" Google\r\n\t ",
        utm_campaign="spring_leads_" + "x" * 200,
        utm_medium="cpc",
    )
    assert attr.utm_source == "Google"
    assert len(attr.utm_campaign) == 120
    assert attr.utm_medium == "cpc"


def test_event_request_validation():
    # Valid payload
    event = EventRequest(
        event_name="whatsapp_click",
        event_id="evt_valid_12345",
        occurred_at=datetime.now(timezone.utc),
        lead_reference="lead_123",
    )
    assert event.event_name == "whatsapp_click"
    assert event.event_id == "evt_valid_12345"

    # Invalid event name
    with pytest.raises(ValidationError):
        EventRequest(
            event_name="invalid_custom_event",  # type: ignore
            event_id="evt_invalid",
            occurred_at=datetime.now(timezone.utc),
        )


def test_lead_request_validation():
    lead = LeadRequest(
        lead_reference="lead_test_001",
        contact=LeadContactData(
            first_name="Jane",
            last_name="Doe",
            phone="+923167417135",
            email="jane@example.com",
        ),
        lead_status="qualified",
    )
    assert lead.contact.first_name == "Jane"
    assert lead.lead_status == "qualified"
