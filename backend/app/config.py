"""Configuration module for WhatsApp Attribution Router."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core Application
    app_name: str = "WhatsApp Attribution Router"
    app_version: str = "1.0.0"
    env: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    api_key: str = "war_dev_secret_key_12345"
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 120
    max_request_body_bytes: int = 524288  # 512 KB

    # Google Sheets Integration
    google_sheets_enabled: bool = False
    google_sheets_spreadsheet_id: str = ""
    google_sheets_worksheet_name: str = "Attribution Leads"
    google_service_account_json: Optional[str] = None
    google_application_credentials: Optional[str] = None

    # GoHighLevel (GHL) CRM Integration
    ghl_enabled: bool = False
    ghl_api_key: Optional[str] = None
    ghl_location_id: Optional[str] = None
    ghl_api_base_url: str = "https://services.leadconnectorhq.com"

    # Outbound Webhook Integration
    outbound_webhook_enabled: bool = False
    outbound_webhook_url: Optional[str] = None
    outbound_webhook_secret: Optional[str] = None
    outbound_webhook_timeout_seconds: float = 10.0
    outbound_webhook_max_retries: int = 3


settings = Settings()
