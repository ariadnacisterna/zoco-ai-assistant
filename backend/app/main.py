from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    CORS_ALLOWED_HEADERS,
    CORS_ALLOWED_METHODS,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title=APP_NAME,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )

    frontend_origin = str(settings.frontend_origin).rstrip("/")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin],
        allow_credentials=False,
        allow_methods=CORS_ALLOWED_METHODS,
        allow_headers=CORS_ALLOWED_HEADERS,
    )

    application.include_router(api_router)

    return application


app = create_app()
