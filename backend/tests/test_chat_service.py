import asyncio
from unittest.mock import AsyncMock, Mock

from app.core.constants import (
    CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
    CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
)
from app.core.enums import ChatStatus
from app.core.exceptions import AnswerGenerationError
from app.schemas.knowledge import RetrievedKnowledgeChunk
from app.services.chat_service import ChatService
from app.services.gemini_generation_service import GeminiGenerationService
from app.services.semantic_retrieval_service import SemanticRetrievalService
from tests.constants import (
    TEST_CHAT_ANSWER,
    TEST_CHAT_MESSAGE,
    TEST_FIRST_CHUNK,
    TEST_MAX_MESSAGE_LENGTH,
    TEST_PAGE_TITLE,
    TEST_SOURCE_SIMILARITY,
    TEST_SOURCE_URL,
)


def _create_service(
    chunks: list[RetrievedKnowledgeChunk],
) -> tuple[ChatService, GeminiGenerationService]:
    retrieval_service = Mock(spec=SemanticRetrievalService)
    retrieval_service.search = AsyncMock(return_value=chunks)

    generation_service = Mock(spec=GeminiGenerationService)
    generation_service.generate_answer = AsyncMock(return_value=TEST_CHAT_ANSWER)

    service = ChatService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        max_message_length=TEST_MAX_MESSAGE_LENGTH,
    )

    return service, generation_service


def test_answer_returns_grounded_answer_and_sources() -> None:
    chunks = [
        RetrievedKnowledgeChunk(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=0,
            similarity=TEST_SOURCE_SIMILARITY,
        )
    ]
    service, generation_service = _create_service(chunks)

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE))

    assert response.status == ChatStatus.ANSWERED
    assert response.answer == TEST_CHAT_ANSWER
    assert len(response.sources) == 1
    assert str(response.sources[0].source_url) == TEST_SOURCE_URL
    generation_service.generate_answer.assert_awaited_once_with(
        TEST_CHAT_MESSAGE,
        chunks,
    )


def test_answer_uses_human_fallback_without_relevant_context() -> None:
    service, generation_service = _create_service([])

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE))

    assert response.status == ChatStatus.HUMAN_FALLBACK
    assert response.answer == CHAT_INSUFFICIENT_CONTEXT_MESSAGE
    assert response.sources == []
    generation_service.generate_answer.assert_not_awaited()


def test_answer_uses_human_fallback_when_generation_fails() -> None:
    chunks = [
        RetrievedKnowledgeChunk(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=0,
            similarity=TEST_SOURCE_SIMILARITY,
        )
    ]
    service, generation_service = _create_service(chunks)
    generation_service.generate_answer.side_effect = AnswerGenerationError()

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE))

    assert response.status == ChatStatus.HUMAN_FALLBACK
    assert response.answer == CHAT_PROVIDER_UNAVAILABLE_MESSAGE
    assert response.sources == []
