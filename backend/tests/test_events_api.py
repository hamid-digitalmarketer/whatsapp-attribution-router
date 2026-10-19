"""Tests for public browser attribution events API."""

from datetime import datetime, timezone

from app.security import rate_limiter


def test_ingest_valid_whatsapp_click(client):
    payload = {
        "event_name": "whatsapp_click",
        "event_id": "evt_test_ingest_001",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "lead_reference": "lead_test_001",
        "attribution": {
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "lahore_leads",
        },
        "page": {
            "landing_page": "https://example.com/landing",
            "referrer": "https://google.com/",
        },
        "destination": {
            "type": "whatsapp",
            "phone_number": "923167417135",
            "button_id": "hero_cta",
        },
    }

    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["event_id"] == "evt_test_ingest_001"
    assert data["lead_reference"] == "lead_test_001"
    assert data["deduplicated"] is False


def test_event_deduplication(client):
    payload = {
        "event_name": "whatsapp_click",
        "event_id": "evt_duplicate_test_999",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "lead_reference": "lead_duplicate_test",
    }

    # First attempt - accepted
    resp1 = client.post("/api/v1/events", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["deduplicated"] is False

    # Second attempt with identical event_id - deduplicated
    resp2 = client.post("/api/v1/events", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["deduplicated"] is True
    assert data2["status"] == "deduplicated"


def test_rate_limiting_enforcement(client):
    rate_limiter.limit = 3
    payload = {
        "event_name": "whatsapp_click",
        "event_id": "evt_rate_limit_1",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }

    # First 3 requests succeed
    for i in range(3):
        payload["event_id"] = f"evt_rate_{i}"
        resp = client.post("/api/v1/events", json=payload)
        assert resp.status_code == 200

    # 4th request exceeds rate limit
    payload["event_id"] = "evt_rate_exceeded"
    resp = client.post("/api/v1/events", json=payload)
    assert resp.status_code == 429
    assert "Rate limit exceeded" in resp.json()["detail"]


def test_event_validation_error(client):
    # Missing required event_id
    payload = {
        "event_name": "whatsapp_click",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 422
