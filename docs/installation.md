# Installation & Integration Guide

## 1. Browser Library Integration

### Option A: Static HTML Script Tag
Include `attribution-router.js` before your closing `</body>` tag:

```html
<script src="path/to/attribution-router.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    const router = new WhatsAppAttributionRouter({
      phoneNumber: '923167417135',
      storageType: 'sessionStorage',
      attributionModel: 'last_touch',
      buttonSelector: '[data-wa-button]',
      apiEndpoint: 'https://api.yourdomain.com/api/v1/events'
    });

    router.init();
  });
</script>
```

### Option B: CommonJS / Node Module
```javascript
const WhatsAppAttributionRouter = require('whatsapp-attribution-router');

const router = new WhatsAppAttributionRouter({
  phoneNumber: '923167417135',
  storageType: 'sessionStorage'
});
```

---

## 2. Python Backend Setup

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running Locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Health Check
```bash
curl http://localhost:8000/health
```
