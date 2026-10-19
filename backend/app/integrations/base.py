"""Base integration interface for WhatsApp Attribution Router."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.schemas import EventRequest, LeadRequest


class BaseIntegration(ABC):
    """Abstract base class for all downstream destination integrations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the integration destination."""
        pass

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Whether this integration is enabled in configuration."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether all necessary credentials and settings are present."""
        pass

    @abstractmethod
    async def dispatch_event(self, event: EventRequest) -> Dict[str, Any]:
        """Dispatches an attribution event to the destination."""
        pass

    @abstractmethod
    async def dispatch_lead(self, lead: LeadRequest) -> Dict[str, Any]:
        """Dispatches or updates a CRM lead record."""
        pass
