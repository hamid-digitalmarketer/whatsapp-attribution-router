# GoHighLevel (GHL) CRM Integration Guide

WhatsApp Attribution Router integrates with the GoHighLevel LeadConnector v2 API to create and update contact attribution.

## Key Principles & Privacy Controls

1. **No Fake Ghost Contacts:** An anonymous WhatsApp button click does **not** create a fake contact with a dummy email or telephone number.
2. **Two-Stage Workflow:**
   - **Stage 1 (Click):** An anonymous attribution event is logged to Google Sheets and webhooks. Contact creation in GHL is deferred until genuine customer details exist.
   - **Stage 2 (Lead Submission):** When the customer sends an inbound message or fills out an intake form, `POST /api/v1/leads` is called with their verified phone/email and `lead_reference`.
3. **Attribution Tagging:**
   The contact is tagged automatically:
   - `WhatsApp Lead`
   - `Source: <utm_source>`
   - `Campaign: <utm_campaign>`
   - `Status: <lead_status>`
4. **Custom Fields Mapping:**
   Maps parameters to custom fields (`lead_reference`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`).

## Configuration

Set the following environment variables:

```env
GHL_ENABLED=true
GHL_API_KEY=your_ghl_v2_api_key_or_oauth_token
GHL_LOCATION_ID=your_ghl_location_id
GHL_API_BASE_URL=https://services.leadconnectorhq.com
```
