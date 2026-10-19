"""Security, authentication, and rate limiting module."""

import secrets
import time
from collections import defaultdict
from threading import Lock
from typing import Optional

from fastapi import Header, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


class RateLimiter:
    """Thread-safe sliding-window in-memory rate limiter per client IP."""

    def __init__(self, limit_per_minute: int = 120):
        self.limit = limit_per_minute
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        with self.lock:
            timestamps = self.requests[client_ip]
            # Prune timestamps older than 60 seconds
            valid_timestamps = [t for t in timestamps if t > window_start]
            if len(valid_timestamps) >= self.limit:
                self.requests[client_ip] = valid_timestamps
                return False

            valid_timestamps.append(now)
            self.requests[client_ip] = valid_timestamps
            return True

    def reset(self):
        with self.lock:
            self.requests.clear()


rate_limiter = RateLimiter(settings.rate_limit_per_minute)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejects incoming HTTP requests with bodies exceeding the configured maximum size."""

    def __init__(self, app, max_bytes: int = 524288):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_bytes:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": f"Request body exceeds maximum size of {self.max_bytes} bytes."
                        },
                    )
            except ValueError:
                pass
        return await call_next(request)


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> bool:
    """Verifies API key from X-API-Key header or Bearer token using constant-time comparison."""
    token = None
    if x_api_key:
        token = x_api_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    if not token or not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not secrets.compare_digest(token, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def mask_secret(val: Optional[str]) -> str:
    """Safely masks sensitive credentials for safe operational status responses."""
    if not val:
        return ""
    s = str(val).strip()
    if len(s) <= 8:
        return "********"
    return f"{s[:4]}...{s[-4:]}"
