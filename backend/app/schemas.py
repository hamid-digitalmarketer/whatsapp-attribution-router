"""Data schemas for WhatsApp Attribution Router."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class AttributionData(BaseModel):
    model: Optional[str] = "last_touch"
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    gclid: Optional[str] = None
    gbraid: Optional[str] = None
    wbraid: Optional[str] = None
    fbclid: Optional[str] = None

    @field_validator(
        "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", mode="before"
    )
    @classmethod
    def sanitize_field(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        s = str(v).strip()
        # Enforce reasonable length and strip control characters
        s = s.replace("\r", "").replace("\n", "").replace("\t", " ")
        return s[:120] if s else None


class PageData(BaseModel):
    landing_page: Optional[str] = Field(None, max_length=500)
    referrer: Optional[str] = Field(None, max_length=500)


class DestinationData(BaseModel):
    type: str = "whatsapp"
    phone_number: Optional[str] = Field(None, max_length=32)
    button_id: Optional[str] = Field("default", max_length=64)


AllowedEventNames = Literal[
    "whatsapp_click",
    "landing_page_view",
    "attribution_captured",
    "lead_submitted",
    "lead_status_updated",
]


class EventRequest(BaseModel):
    event_name: AllowedEventNames
    event_id: str = Field(..., min_length=3, max_length=128)
    occurred_at: datetime
    lead_reference: Optional[str] = Field(None, max_length=128)
    session_id: Optional[str] = Field(None, max_length=128)
    attribution: Optional[AttributionData] = None
    page: Optional[PageData] = None
    destination: Optional[DestinationData] = None
    custom_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EventResponse(BaseModel):
    status: str = "accepted"
    event_id: str
    lead_reference: Optional[str] = None
    deduplicated: bool = False
    dispatched_destinations: List[str] = Field(default_factory=list)
    destination_results: Dict[str, Any] = Field(default_factory=dict)


class LeadContactData(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=32)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=150)


class LeadRequest(BaseModel):
    lead_reference: str = Field(..., min_length=3, max_length=128)
    contact: LeadContactData
    lead_status: str = Field("new", max_length=64)
    attribution: Optional[AttributionData] = None
    notes: Optional[str] = Field(None, max_length=1000)


class LeadResponse(BaseModel):
    status: str = "processed"
    lead_reference: str
    crm_id: Optional[str] = None
    destination_results: Dict[str, Any] = Field(default_factory=dict)


class IntegrationStatusItem(BaseModel):
    enabled: bool
    configured: bool
    status: Literal["ready", "unconfigured", "disabled"]
    details: Dict[str, Any] = Field(default_factory=dict)


class IntegrationsStatusResponse(BaseModel):
    google_sheets: IntegrationStatusItem
    gohighlevel: IntegrationStatusItem
    outbound_webhook: IntegrationStatusItem
