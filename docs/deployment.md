# Deployment Guide

WhatsApp Attribution Router separates frontend static assets from the Python backend API.

## Frontend Demo Deployment (GitHub Pages / Firebase Hosting / Vercel / Netlify)
The frontend demo consists of static HTML, CSS, and vanilla JS in `demo/` and `src/`.
- **GitHub Pages:** Set source branch to `main` with directory `/demo` or build folder.
- **Firebase Hosting:**
  ```json
  {
    "hosting": {
      "public": "demo",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
    }
  }
  ```

---

## Backend API Deployment (Docker / Cloud Run / Render)

### Docker Deployment
A minimal Dockerfile for the Python backend:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Run
```bash
docker build -t whatsapp-attribution-router .
docker run -p 8000:8000 --env-file .env whatsapp-attribution-router
```
