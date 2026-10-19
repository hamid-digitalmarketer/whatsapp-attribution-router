"""Tests for protected leads submission API."""


def test_leads_endpoint_requires_authentication(client):
    payload = {
        "lead_reference": "lead_test_auth",
        "contact": {"phone": "+923167417135"},
        "lead_status": "new",
    }
    # No auth header
    response = client.post("/api/v1/leads", json=payload)
    assert response.status_code == 401

    # Invalid API key
    response = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"X-API-Key": "wrong_key"},
    )
    assert response.status_code == 401


def test_leads_endpoint_success_with_valid_key(client):
    payload = {
        "lead_reference": "lead_valid_001",
        "contact": {
            "first_name": "Hamid",
            "last_name": "Marketer",
            "phone": "+923167417135",
            "email": "lead@example.com",
            "company": "E-Commerce Agency",
        },
        "lead_status": "qualified",
        "attribution": {
            "utm_source": "meta",
            "utm_medium": "cpc",
            "utm_campaign": "cro_audit_offer",
        },
        "notes": "Verified client looking for WhatsApp attribution setup.",
    }

    # Test with X-API-Key header
    response = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"X-API-Key": "war_dev_secret_key_12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["lead_reference"] == "lead_valid_001"

    # Test with Authorization: Bearer header
    payload["lead_reference"] = "lead_valid_002"
    response2 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": "Bearer war_dev_secret_key_12345"},
    )
    assert response2.status_code == 200
