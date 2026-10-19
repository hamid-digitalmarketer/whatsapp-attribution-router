# Troubleshooting Guide & FAQs

### 1. WhatsApp Button Does Not Open Pre-filled Text
- **Cause:** Phone number format contains plus signs, spaces, or leading national zeros.
- **Fix:** The library normalizes numbers automatically, but ensure standard E.164 digits without plus (e.g., `923167417135`).

### 2. Events Are Not Reaching the Backend
- **Check 1:** Verify CORS settings in `backend/.env`: `CORS_ORIGINS=["https://yourdomain.com"]`.
- **Check 2:** Verify browser network tab for `POST /api/v1/events` returning 200.
- **Check 3:** Ensure rate limiting (120 req/min) has not been exceeded during testing.

### 3. Duplicate Rows in Google Sheets
- **Check:** Ensure deduplication is active. The backend deduplicates identical `event_id` strings within a 48-hour window.

### 4. Direct Traffic Overwriting Paid Campaign UTMs
- **Explanation:** By design, WhatsApp Attribution Router **preserves** active campaign attribution when a user browses other pages on your site directly without query parameters.
