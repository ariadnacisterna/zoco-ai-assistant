import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    APPLICATION_LOGGER_NAME,
    CORS_ALLOWED_HEADERS,
    CORS_ALLOWED_METHODS,
    UVICORN_LOGGER_NAME,
)
from app.database.mongodb import MongoDatabase
from app.services.knowledge_factory import (
    create_embedding_service,
    create_knowledge_service,
    create_semantic_retrieval_service,
)
from app.services.knowledge_scheduler import KnowledgeScheduler


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources."""

    application_logger = logging.getLogger(APPLICATION_LOGGER_NAME)
    uvicorn_logger = logging.getLogger(UVICORN_LOGGER_NAME)

    application_logger.handlers = list(uvicorn_logger.handlers)
    application_logger.setLevel(logging.INFO)
    application_logger.propagate = False

    settings = get_settings()
    mongo_database = MongoDatabase(settings)

    embedding_service = create_embedding_service(settings)
    knowledge_service = create_knowledge_service(
        settings,
        mongo_database,
        embedding_service,
    )
    semantic_retrieval_service = create_semantic_retrieval_service(
        settings,
        mongo_database,
        embedding_service,
    )
    knowledge_scheduler = KnowledgeScheduler(
        knowledge_service,
        settings.update_interval_hours,
    )

    application.state.mongo_database = mongo_database
    application.state.knowledge_service = knowledge_service
    application.state.semantic_retrieval_service = semantic_retrieval_service

    knowledge_scheduler.start()

    try:
        yield
    finally:
        await knowledge_scheduler.stop()
        await embedding_service.close()
        await mongo_database.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    application = FastAPI(
        title=APP_NAME,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        lifespan=lifespan,
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
