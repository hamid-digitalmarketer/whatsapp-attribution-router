"""Event deduplication service with TTL window."""

import time
from threading import Lock
from typing import Dict


class DeduplicationService:
    """Thread-safe in-memory deduplication store with 48-hour TTL window."""

    def __init__(self, ttl_seconds: int = 172800):  # 48 hours
        self.ttl = ttl_seconds
        self._store: Dict[str, float] = {}
        self._lock = Lock()

    def is_duplicate(self, event_id: str) -> bool:
        now = time.time()
        with self._lock:
            recorded_at = self._store.get(event_id)
            if recorded_at is None:
                return False
            if now - recorded_at > self.ttl:
                del self._store[event_id]
                return False
            return True

    def record(self, event_id: str) -> bool:
        """Records event_id. Returns True if successfully recorded (new), False if duplicate."""
        now = time.time()
        with self._lock:
            # Periodic cleanup if store grows large
            if len(self._store) > 10000:
                cutoff = now - self.ttl
                self._store = {k: v for k, v in self._store.items() if v > cutoff}

            recorded_at = self._store.get(event_id)
            if recorded_at is not None and (now - recorded_at <= self.ttl):
                return False

            self._store[event_id] = now
            return True

    def clear(self):
        with self._lock:
            self._store.clear()


deduplication_service = DeduplicationService()
