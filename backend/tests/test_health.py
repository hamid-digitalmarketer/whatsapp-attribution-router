"""Tests for health endpoint and integrations status."""

from app.config import settings


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == settings.app_name
    assert data["version"] == settings.app_version
    assert "timestamp" in data


def test_integrations_status_endpoint(client):
    response = client.get("/api/v1/integrations/status")
    assert response.status_code == 200
    data = response.json()
    assert "google_sheets" in data
    assert "gohighlevel" in data
    assert "outbound_webhook" in data
    assert data["google_sheets"]["status"] in {"ready", "unconfigured", "disabled"}
    assert data["gohighlevel"]["status"] in {"ready", "unconfigured", "disabled"}
    assert data["outbound_webhook"]["status"] in {"ready", "unconfigured", "disabled"}
