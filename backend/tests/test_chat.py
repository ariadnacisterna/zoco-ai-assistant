from unittest.mock import AsyncMock

from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import get_chat_service
from app.core.constants import API_PREFIX, CHAT_PATH
from app.core.enums import ChatStatus
from app.main import app
from app.schemas.chat import ChatResponse, ChatSource
from app.services.chat_service import ChatService
from tests.constants import (
    TEST_CHAT_ANSWER,
    TEST_CHAT_MESSAGE,
    TEST_CONVERSATION_ID,
    TEST_PAGE_TITLE,
    TEST_SOURCE_SIMILARITY,
    TEST_SOURCE_URL,
)

client = TestClient(app)


def test_chat_returns_grounded_answer() -> None:
    expected_response = ChatResponse(
        conversation_id=TEST_CONVERSATION_ID,
        status=ChatStatus.ANSWERED,
        answer=TEST_CHAT_ANSWER,
        sources=[
            ChatSource(
                source_url=TEST_SOURCE_URL,
                title=TEST_PAGE_TITLE,
                similarity=TEST_SOURCE_SIMILARITY,
            )
        ],
    )
    chat_service = AsyncMock(spec=ChatService)
    chat_service.answer.return_value = expected_response
    app.dependency_overrides[get_chat_service] = lambda: chat_service

    try:
        response = client.post(
            f"{API_PREFIX}{CHAT_PATH}",
            json={
                "message": TEST_CHAT_MESSAGE,
                "conversation_id": str(TEST_CONVERSATION_ID),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(mode="json")
    chat_service.answer.assert_awaited_once_with(
        TEST_CHAT_MESSAGE,
        TEST_CONVERSATION_ID,
    )
