from unittest.mock import AsyncMock

from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import get_health_service
from app.core.constants import API_PREFIX, HEALTH_PATH
from app.core.enums import DatabaseStatus, KnowledgeStatus, ServiceStatus
from app.main import app
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

client = TestClient(app)


def test_health_endpoint_returns_ok_when_database_is_connected() -> None:
    expected_response = HealthResponse(
        status=ServiceStatus.OK,
        database=DatabaseStatus.CONNECTED,
        knowledge=KnowledgeStatus.EMPTY,
    )

    health_service = AsyncMock(spec=HealthService)
    health_service.get_health_status.return_value = expected_response

    app.dependency_overrides[get_health_service] = lambda: health_service

    try:
        response = client.get(f"{API_PREFIX}{HEALTH_PATH}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(mode="json")


def test_health_endpoint_returns_503_when_database_is_disconnected() -> None:
    expected_response = HealthResponse(
        status=ServiceStatus.ERROR,
        database=DatabaseStatus.DISCONNECTED,
        knowledge=KnowledgeStatus.UNAVAILABLE,
    )

    health_service = AsyncMock(spec=HealthService)
    health_service.get_health_status.return_value = expected_response

    app.dependency_overrides[get_health_service] = lambda: health_service

    try:
        response = client.get(f"{API_PREFIX}{HEALTH_PATH}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == expected_response.model_dump(mode="json")
