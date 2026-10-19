# Privacy, Security & Compliance

WhatsApp Attribution Router is engineered with privacy as a foundational requirement.

## 1. Zero Fingerprinting
The library does **not** inspect canvas hashes, audio context, installed fonts, or WebGL parameters.

## 2. Configurable Browser Storage
- `sessionStorage` (Default): Attribution data exists strictly while the browser tab remains open. Clears automatically when the tab is closed.
- `localStorage`: Persists attribution across navigation on the same domain.
- `none` (Memory Only): Zero persistent browser storage. Stored in memory variables during the page lifetime.

## 3. Consent Management Integration
When `requireConsent: true` is configured, the library verifies consent before writing to any persistent storage:

```javascript
const router = new WhatsAppAttributionRouter({
  requireConsent: true,
  hasConsent: () => window.CookieConsent && window.CookieConsent.hasAnalyticsConsent()
});
```

## 4. No PII in Browser Storage or WhatsApp URL
- Personal identifiers (names, emails, credit card data, passwords) are never stored in browser storage.
- WhatsApp prefilled messages contain only sanitized campaign labels and an opaque, non-sensitive lead reference ID (`lead_...`).

## 5. Security Perimeters
- **API Key Protection:** Administrative lead submissions via `POST /api/v1/leads` require constant-time API key verification (`X-API-Key` or `Bearer` token).
- **Rate Limiting:** Public `/api/v1/events` endpoint enforces sliding-window rate limits (120 req/min per IP).
- **Body Size Caps:** Payloads larger than 512 KB are rejected with HTTP 413.
- **SSRF Prevention:** Webhook endpoints must be defined strictly in server-side configuration; public requests cannot supply arbitrary destination URLs.
