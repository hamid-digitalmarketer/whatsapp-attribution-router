"""FastAPI main application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.events import router as events_router
from app.routes.health import router as health_router
from app.routes.integrations import router as integrations_router
from app.routes.leads import router as leads_router
from app.security import RequestSizeLimitMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Privacy-conscious marketing attribution gateway capturing UTM parameters, "
            "routing WhatsApp inquiries, and forwarding events to Google Sheets & GoHighLevel CRM."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Request body size limit
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_bytes=settings.max_request_body_bytes,
    )

    # Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(health_router)
    app.include_router(events_router)
    app.include_router(leads_router)
    app.include_router(integrations_router)

    return app


app = create_app()
