"""Tests for DeduplicationService."""

from app.services.deduplication import DeduplicationService


def test_deduplication_lifecycle():
    service = DeduplicationService(ttl_seconds=10)

    # First record should be new
    assert service.record("evt_test_1") is True
    assert service.is_duplicate("evt_test_1") is True

    # Duplicate should return False
    assert service.record("evt_test_1") is False

    # Different event ID is new
    assert service.record("evt_test_2") is True


def test_deduplication_ttl_expiration():
    service = DeduplicationService(ttl_seconds=0.05)
    service.record("evt_expiring")

    assert service.is_duplicate("evt_expiring") is True

    # Sleep slightly past TTL
    import time

    time.sleep(0.06)

    assert service.is_duplicate("evt_expiring") is False
    assert service.record("evt_expiring") is True
