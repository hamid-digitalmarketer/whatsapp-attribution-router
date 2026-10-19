# Google Sheets Integration Guide

WhatsApp Attribution Router can stream attributed WhatsApp clicks and verified lead updates directly to a Google Sheets spreadsheet.

## Column Schema

When configured, the adapter writes rows matching the following schema:

| Column Index | Field Name | Description |
| :--- | :--- | :--- |
| `A` | `timestamp` | ISO 8601 UTC timestamp of click or lead update |
| `B` | `event_id` | Unique click event identifier (e.g. `evt_...`) |
| `C` | `event_name` | Event type (`whatsapp_click`, `lead_status_updated`) |
| `D` | `lead_reference` | Opaque lead identifier (e.g. `lead_...`) |
| `E` | `utm_source` | Traffic source (`google`, `facebook`, `tiktok`) |
| `F` | `utm_medium` | Marketing medium (`cpc`, `paid_social`, `email`) |
| `G` | `utm_campaign` | Advertising campaign name |
| `H` | `utm_content` | Ad variant or creative identifier |
| `I` | `utm_term` | Paid search query or keyword |
| `J` | `landing_page` | URL of the page where the button was clicked |
| `K` | `referrer` | HTTP referrer URL |
| `L` | `whatsapp_button_id` | Identifier of the clicked CTA button |
| `M` | `destination_phone` | Target WhatsApp recipient number |
| `N` | `lead_status` | Status (`unconfirmed_click`, `qualified`, `converted`) |

## Setup Instructions

1. Create a Google Cloud project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API**.
3. Create a **Service Account** and download its JSON key file.
4. Create a Google Spreadsheet and share it with the service account email (giving it **Editor** permissions).
5. Set environment variables:
   ```env
   GOOGLE_SHEETS_ENABLED=true
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
   GOOGLE_SHEETS_WORKSHEET_NAME="Attribution Leads"
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```
