"""Attribution normalization and channel classification service."""

from typing import Any, Dict, Optional

from app.schemas import AttributionData


def classify_channel_group(source: Optional[str], medium: Optional[str]) -> str:
    """Classifies source and medium into standard marketing channel groupings."""
    src = (source or "").lower().strip()
    med = (medium or "").lower().strip()

    if not src and not med:
        return "Direct / Unattributed"

    social_sources = [
        "facebook",
        "meta",
        "instagram",
        "tiktok",
        "linkedin",
        "twitter",
        "x",
        "pinterest",
    ]
    is_social_source = any(s in src for s in social_sources)

    if is_social_source and med in {
        "cpc",
        "ppc",
        "paid_social",
        "paidsocial",
        "cpm",
        "social",
        "feed",
    }:
        return "Paid Social"

    if med in {"paid_social", "paidsocial", "cpm"}:
        return "Paid Social"

    if (
        med in {"cpc", "ppc", "paidsearch"}
        or any(s in src for s in ["google", "bing"])
        and med == "cpc"
    ):
        return "Paid Search"

    if (
        med == "organic"
        or any(s in src for s in ["google", "bing", "yahoo", "duckduckgo"])
        and not med
    ):
        return "Organic Search"

    if med in {"email", "newsletter", "e-mail"}:
        return "Email"

    if med in {"referral", "affiliate", "partner"}:
        return "Referral / Affiliate"

    if med in {"social", "organic_social"}:
        return "Organic Social"

    return "Other Campaign"


def normalize_attribution_payload(attribution: Optional[AttributionData]) -> Dict[str, Any]:
    """Normalizes and extracts enriched attribution dictionary."""
    if not attribution:
        return {
            "model": "last_touch",
            "utm_source": None,
            "utm_medium": None,
            "utm_campaign": None,
            "utm_content": None,
            "utm_term": None,
            "gclid": None,
            "gbraid": None,
            "wbraid": None,
            "fbclid": None,
            "channel_group": "Direct / Unattributed",
        }

    src = attribution.utm_source.lower().strip() if attribution.utm_source else None
    med = attribution.utm_medium.lower().strip() if attribution.utm_medium else None
    channel = classify_channel_group(src, med)

    return {
        "model": attribution.model or "last_touch",
        "utm_source": src,
        "utm_medium": med,
        "utm_campaign": attribution.utm_campaign,
        "utm_content": attribution.utm_content,
        "utm_term": attribution.utm_term,
        "gclid": attribution.gclid,
        "gbraid": attribution.gbraid,
        "wbraid": attribution.wbraid,
        "fbclid": attribution.fbclid,
        "channel_group": channel,
    }
