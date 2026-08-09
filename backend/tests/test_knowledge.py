from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi import status
from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.api.dependencies import get_knowledge_service
from app.core.constants import (
    API_PREFIX,
    DATABASE_UNAVAILABLE_MESSAGE,
    KNOWLEDGE_PATH,
    KNOWLEDGE_SOURCE_UNAVAILABLE_MESSAGE,
)
from app.core.enums import ServiceStatus
from app.core.exceptions import KnowledgeSourceUnavailableError
from app.main import app
from app.schemas.knowledge import KnowledgeUpdateResponse
from app.services.knowledge_service import KnowledgeService

client = TestClient(app)

TEST_UPDATED_AT = datetime(2026, 8, 9, tzinfo=UTC)


def test_update_knowledge_returns_ok() -> None:
    expected_response = KnowledgeUpdateResponse(
        status=ServiceStatus.OK,
        pages_processed=3,
        chunks_stored=8,
        updated_at=TEST_UPDATED_AT,
    )

    knowledge_service = AsyncMock(spec=KnowledgeService)
    knowledge_service.update_knowledge.return_value = expected_response

    app.dependency_overrides[get_knowledge_service] = lambda: knowledge_service

    try:
        response = client.put(f"{API_PREFIX}{KNOWLEDGE_PATH}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(mode="json")


def test_update_knowledge_returns_502_when_source_fails() -> None:
    knowledge_service = AsyncMock(spec=KnowledgeService)
    knowledge_service.update_knowledge.side_effect = KnowledgeSourceUnavailableError()

    app.dependency_overrides[get_knowledge_service] = lambda: knowledge_service

    try:
        response = client.put(f"{API_PREFIX}{KNOWLEDGE_PATH}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert response.json() == {"detail": KNOWLEDGE_SOURCE_UNAVAILABLE_MESSAGE}


def test_update_knowledge_returns_503_when_database_fails() -> None:
    knowledge_service = AsyncMock(spec=KnowledgeService)
    knowledge_service.update_knowledge.side_effect = PyMongoError()

    app.dependency_overrides[get_knowledge_service] = lambda: knowledge_service

    try:
        response = client.put(f"{API_PREFIX}{KNOWLEDGE_PATH}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"detail": DATABASE_UNAVAILABLE_MESSAGE}
