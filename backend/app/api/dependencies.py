from typing import Annotated

from fastapi import Depends, Request

from app.database.dependencies import get_mongo_database
from app.database.mongodb import MongoDatabase
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService
from app.services.knowledge_service import KnowledgeService


def get_health_service(
    mongo_database: Annotated[
        MongoDatabase,
        Depends(get_mongo_database),
    ],
) -> HealthService:
    """Build the health service with its dependencies."""

    health_repository = HealthRepository(mongo_database)

    return HealthService(health_repository)


def get_knowledge_service(request: Request) -> KnowledgeService:
    """Return the shared knowledge service."""

    return request.app.state.knowledge_service
