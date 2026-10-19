"""Event processing and destination dispatch orchestrator."""

import logging
from typing import Dict, List, Optional

from app.integrations.base import BaseIntegration
from app.integrations.gohighlevel import gohighlevel_integration
from app.integrations.google_sheets import google_sheets_integration
from app.integrations.webhook import webhook_integration
from app.schemas import EventRequest, EventResponse, LeadRequest, LeadResponse
from app.services.deduplication import deduplication_service

logger = logging.getLogger(__name__)


class EventProcessor:
    """Coordinates deduplication and delivery to enabled downstream destinations."""

    def __init__(self, integrations: Optional[List[BaseIntegration]] = None):
        self.integrations = integrations or [
            google_sheets_integration,
            gohighlevel_integration,
            webhook_integration,
        ]

    async def process_event(self, event: EventRequest) -> EventResponse:
        # Check deduplication window
        if deduplication_service.is_duplicate(event.event_id):
            return EventResponse(
                status="deduplicated",
                event_id=event.event_id,
                lead_reference=event.lead_reference,
                deduplicated=True,
                dispatched_destinations=[],
                destination_results={"info": "Duplicate event suppressed within 48h TTL window."},
            )

        # Record event in deduplication store
        deduplication_service.record(event.event_id)

        dispatched: List[str] = []
        results: Dict[str, dict] = {}

        for integration in self.integrations:
            if integration.enabled and integration.is_configured():
                try:
                    res = await integration.dispatch_event(event)
                    dispatched.append(integration.name)
                    results[integration.name] = res
                except Exception as exc:
                    logger.error(
                        "Error dispatching event %s to %s: %s",
                        event.event_id,
                        integration.name,
                        str(exc),
                    )
                    results[integration.name] = {"status": "error", "detail": str(exc)}

        return EventResponse(
            status="accepted",
            event_id=event.event_id,
            lead_reference=event.lead_reference,
            deduplicated=False,
            dispatched_destinations=dispatched,
            destination_results=results,
        )

    async def process_lead(self, lead: LeadRequest) -> LeadResponse:
        results: Dict[str, dict] = {}
        crm_id: Optional[str] = None

        for integration in self.integrations:
            if integration.enabled and integration.is_configured():
                try:
                    res = await integration.dispatch_lead(lead)
                    results[integration.name] = res
                    if integration.name == "gohighlevel" and res.get("status") == "success":
                        crm_id = res.get("contact_id")
                except Exception as exc:
                    logger.error(
                        "Error dispatching lead %s to %s: %s",
                        lead.lead_reference,
                        integration.name,
                        str(exc),
                    )
                    results[integration.name] = {"status": "error", "detail": str(exc)}

        return LeadResponse(
            status="processed",
            lead_reference=lead.lead_reference,
            crm_id=crm_id,
            destination_results=results,
        )


event_processor = EventProcessor()
