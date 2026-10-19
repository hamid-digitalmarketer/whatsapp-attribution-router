"""Test configuration and fixtures for backend test suite."""

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.security import rate_limiter
from app.services.deduplication import deduplication_service


@pytest.fixture(autouse=True)
def reset_state():
    """Resets rate limiter and deduplication service before every test."""
    rate_limiter.reset()
    deduplication_service.clear()
    settings.api_key = "war_dev_secret_key_12345"
    yield
    rate_limiter.reset()
    deduplication_service.clear()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)
