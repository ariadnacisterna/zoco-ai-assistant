from http import HTTPMethod

from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.constants import APP_NAME, DOCS_PATH
from app.main import app

client = TestClient(app)


def test_docs_endpoint() -> None:
    response = client.get(DOCS_PATH)
    assert response.status_code == status.HTTP_200_OK


def test_application_title() -> None:
    assert app.title == APP_NAME


def test_cors_preflight_request() -> None:
    settings = get_settings()
    allowed_origin = str(settings.frontend_origin).rstrip("/")

    response = client.options(
        DOCS_PATH,
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": HTTPMethod.GET,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert HTTPMethod.GET in response.headers["access-control-allow-methods"]
