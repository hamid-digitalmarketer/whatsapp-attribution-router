# Attribution Models & Tracking Semantics

## Attribution Models Supported

### 1. Last Touch (`last_touch` — Default)
- **Behavior:** The most recent campaign visit takes precedence.
- **Use Case:** Direct response campaigns where the final ad clicked before initiating a conversation receives attribution.
- **Direct Traffic Rule:** If a user returns via direct navigation (no UTM parameters), the router **preserves** the existing campaign record rather than overwriting it with blank direct data.

### 2. First Touch (`first_touch`)
- **Behavior:** The initial discovery campaign that introduced the user to the brand is preserved permanently in the session or storage window.
- **Use Case:** High-consideration purchases (real estate, B2B services, enterprise consulting) where initial discovery is the critical metric.

### 3. Multi-Touch Record (`both`)
- **Behavior:** Stores both `first_touch` and `last_touch` objects simultaneously.
- **Use Case:** Advanced analytics teams comparing prospecting ads with retargeting ads.

---

## Technical Honesty & Limitations

> [!IMPORTANT]
> **A WhatsApp click is not proof of a conversation.**
> When a user clicks a WhatsApp button:
> 1. The browser launches the WhatsApp client with prefilled text.
> 2. The user has full control to edit, delete, or choose not to send the message.
> 3. True lead attribution requires downstream matching via CRM or inbound webhook when the message arrives.
