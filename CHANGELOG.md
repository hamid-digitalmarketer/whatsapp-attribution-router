# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-19

### Added
- **Core JavaScript Library (`attribution-router.js`)**:
  - UTM & click ID capture (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `gclid`, `fbclid`).
  - First-touch and last-touch attribution models with fallback protection against direct traffic erasure.
  - Sanitization of parameters to prevent XSS and URL injection.
  - Official WhatsApp click-to-chat URL builder (`https://wa.me/<digits>?text=...`).
  - Pre-filled message templating with campaign references and opaque lead IDs.
  - Storage adapters: `sessionStorage`, `localStorage`, and in-memory fallback.
  - Automatic button binding via `data-wa-button` attributes.
  - Custom DOM events (`whatsapp:click`) and `navigator.sendBeacon` event dispatching.
- **Python FastAPI Gateway (`backend/`)**:
  - Public `POST /api/v1/events` endpoint with IP sliding-window rate limiting (120 req/min).
  - Protected `POST /api/v1/leads` endpoint requiring API key authentication.
  - Health check `GET /health` and safe integrations status `GET /api/v1/integrations/status`.
  - 48-hour event ID deduplication engine.
  - Payload size limiter middleware (512 KB cap).
- **Integrations**:
  - Google Sheets API v4 adapter with automated row appending.
  - GoHighLevel (LeadConnector) v2 CRM adapter with custom fields and tags mapping.
  - Generic outbound webhook with HMAC SHA-256 signature verification.
- **Interactive SaaS Demo (`demo/`)**:
  - Real-time campaign preset simulator, WhatsApp prefilled message preview, and live payload inspector.
- **Automated Test Suite**:
  - 13 Node.js test cases covering URL building, sanitization, and storage lifecycle.
  - 19 Pytest test cases covering schemas, deduplication, rate limiting, and mocked integrations.
  - 100% clean Ruff linting and formatting.
- **CI/CD Workflow (`.github/workflows/ci.yml`)**:
  - Automated Node.js and Python test execution on every push and PR.
