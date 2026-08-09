from fastapi import status
from fastapi.testclient import TestClient

from app.core.constants import APP_NAME, DOCS_PATH
from app.main import app

client = TestClient(app)


def test_docs_endpoint() -> None:
    response = client.get(DOCS_PATH)
    assert response.status_code == status.HTTP_200_OK


def test_application_title() -> None:
    assert app.title == APP_NAME
