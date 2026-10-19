"""Example Python client for submitting verified lead records to WhatsApp Attribution Router."""

import httpx

API_BASE_URL = "http://localhost:8000"
API_KEY = "war_dev_secret_key_12345"


def submit_verified_lead():
    payload = {
        "lead_reference": "lead_sim_abc999",
        "contact": {
            "first_name": "Hamid",
            "last_name": "Consultant",
            "phone": "+923167417135",
            "email": "client@example.com",
            "company": "Performance Marketing Ltd",
        },
        "lead_status": "qualified",
        "attribution": {
            "model": "last_touch",
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "lahore_property_leads",
            "utm_term": "commercial real estate",
        },
        "notes": "Inquiry originated via WhatsApp button click. Client confirmed via inbound chat.",
    }

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }

    with httpx.Client(base_url=API_BASE_URL, timeout=10.0) as client:
        response = client.post("/api/v1/leads", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:", response.json())


if __name__ == "__main__":
    submit_verified_lead()
