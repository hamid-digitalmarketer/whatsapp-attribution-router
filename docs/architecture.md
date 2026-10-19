# System Architecture & Data Flow

WhatsApp Attribution Router (`whatsapp-attribution-router`) bridges top-of-funnel campaign clicks with private, direct WhatsApp messaging conversations and downstream CRM records.

## High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Client ["Browser / Landing Page"]
        User(["Visitor via Ad / Campaign"]) --> Landing["Landing Page (with UTMs)"]
        Landing --> WAR_JS["WhatsApp Attribution Router (JS)"]
        WAR_JS --> Capture["Capture & Normalize UTMs"]
        Capture --> Storage["Session / Local Storage"]
        Storage --> Click{"Visitor Clicks WhatsApp Button"}
        Click -->|Build URL & Prefill| WA_App["WhatsApp Desktop / Mobile App"]
        Click -->|Event Payload| Beacon["sendBeacon / Fetch API"]
    end

    subgraph Backend ["Python FastAPI Gateway"]
        Beacon --> API_Events["POST /api/v1/events"]
        API_Events --> Security["Rate Limiter & Size Checks"]
        Security --> Dedup["Deduplication Engine (48h Window)"]
        Dedup --> Dispatcher["Integration Dispatcher"]
    end

    subgraph Destinations ["Attribution & CRM Destinations"]
        Dispatcher --> GSheets["Google Sheets API v4"]
        Dispatcher --> GHL["GoHighLevel CRM (v2 Contacts)"]
        Dispatcher --> Webhook["Generic Outbound Webhook"]
    end

    subgraph Verified_Lead ["Downstream Conversion Match"]
        WA_App --> Chat["Customer Sends WhatsApp Message"]
        Chat --> SalesRep["Sales Team / CRM Agent"]
        SalesRep --> CRM_Update["POST /api/v1/leads (with lead_reference)"]
        CRM_Update --> GHL
        CRM_Update --> GSheets
    end
```

## Core Components

### 1. Frontend JavaScript Router (`src/attribution-router.js`)
- Runs client-side on your landing page.
- Parses standard attribution query parameters (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `gclid`, `gbraid`, `wbraid`, `fbclid`).
- Isolates first-touch vs. last-touch attribution models.
- Sanitizes input values to prevent header or URL injection.
- Generates official WhatsApp click-to-chat links (`https://wa.me/<number>?text=<encoded_message>`).
- Emits custom DOM events (`whatsapp:click`) for Google Tag Manager, Meta Pixel, or GA4 triggers.

### 2. Python FastAPI Gateway (`backend/app/`)
- Public ingestion endpoint `POST /api/v1/events` for browser click tracking.
- Protected server endpoint `POST /api/v1/leads` for verified sales and CRM lead updates.
- 48-hour event deduplication engine with thread-safe in-memory cache.
- Sliding-window rate limiting (120 req/minute per IP).
- Request body size limiter (512 KB).

### 3. Google Sheets Adapter (`backend/app/integrations/google_sheets.py`)
- Official Google Sheets API v4 append row integration.
- Appends attribution data into standard audit columns.

### 4. GoHighLevel CRM Adapter (`backend/app/integrations/gohighlevel.py`)
- LeadConnector v2 API client.
- Maps campaign parameters, contact details, tags, and custom fields without creating fake ghost contacts.

### 5. Generic Outbound Webhook (`backend/app/integrations/webhook.py`)
- Forwards payloads to any agency CRM or automation tool (e.g. n8n, Make, Zapier).
- HMAC SHA-256 signature verification via `X-WAR-Signature`.
