"""Generic outbound webhook integration adapter."""

import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings
from app.integrations.base import BaseIntegration
from app.schemas import EventRequest, LeadRequest

logger = logging.getLogger(__name__)


class WebhookIntegration(BaseIntegration):
    """Dispatches webhook payloads to trusted, server-configured endpoints."""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self._client = http_client

    @property
    def name(self) -> str:
        return "outbound_webhook"

    @property
    def enabled(self) -> bool:
        return settings.outbound_webhook_enabled

    def is_configured(self) -> bool:
        return bool(
            settings.outbound_webhook_url and settings.outbound_webhook_url.startswith("http")
        )

    def _generate_signature(self, payload_bytes: bytes) -> Optional[str]:
        if not settings.outbound_webhook_secret:
            return None
        secret_bytes = settings.outbound_webhook_secret.encode("utf-8")
        return hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()

    async def _send_payload(self, payload_dict: Dict[str, Any]) -> Dict[str, Any]:
        url = settings.outbound_webhook_url
        payload_json = json.dumps(payload_dict, default=str)
        payload_bytes = payload_json.encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"WhatsApp-Attribution-Router/{settings.app_version}",
        }

        signature = self._generate_signature(payload_bytes)
        if signature:
            headers["X-WAR-Signature"] = signature

        client = self._client or httpx.AsyncClient(
            timeout=settings.outbound_webhook_timeout_seconds
        )
        close_client = self._client is None

        max_retries = max(1, settings.outbound_webhook_max_retries)
        last_error = ""

        try:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, content=payload_bytes, headers=headers)
                    if response.status_code in {200, 201, 202, 204}:
                        return {
                            "status": "success",
                            "attempt": attempt + 1,
                            "status_code": response.status_code,
                        }
                    # 4xx client errors should not be retried
                    if 400 <= response.status_code < 500:
                        return {
                            "status": "error",
                            "status_code": response.status_code,
                            "detail": response.text[:200],
                        }
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_error = str(exc)
                    logger.warning("Webhook attempt %d failed: %s", attempt + 1, last_error)

            return {
                "status": "error",
                "detail": f"Failed after {max_retries} attempts: {last_error}",
            }
        finally:
            if close_client:
                await client.aclose()

    async def dispatch_event(self, event: EventRequest) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "skipped", "reason": "integration_disabled"}
        if not self.is_configured():
            return {"status": "skipped", "reason": "unconfigured_webhook_url"}

        payload = {
            "type": "event",
            "data": event.model_dump(mode="json"),
        }
        return await self._send_payload(payload)

    async def dispatch_lead(self, lead: LeadRequest) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "skipped", "reason": "integration_disabled"}
        if not self.is_configured():
            return {"status": "skipped", "reason": "unconfigured_webhook_url"}

        payload = {
            "type": "lead",
            "data": lead.model_dump(mode="json"),
        }
        return await self._send_payload(payload)


webhook_integration = WebhookIntegration()
