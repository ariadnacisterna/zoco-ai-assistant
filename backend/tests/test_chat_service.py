import asyncio
from unittest.mock import AsyncMock, Mock

from app.core.constants import (
    CHAT_HISTORY_ITEM_TEMPLATE,
    CHAT_HISTORY_SEPARATOR,
    CHAT_HUMAN_FALLBACK_MARKER,
    CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
    CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
    CHAT_RETRIEVAL_QUERY_TEMPLATE,
)
from app.core.enums import ChatStatus, ConversationRole
from app.core.exceptions import AnswerGenerationError
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import ConversationMessage
from app.schemas.knowledge import RetrievedKnowledgeChunk
from app.services.chat_service import ChatService
from app.services.gemini_generation_service import GeminiGenerationService
from app.services.semantic_retrieval_service import SemanticRetrievalService
from tests.constants import (
    TEST_CHAT_ANSWER,
    TEST_CHAT_MESSAGE,
    TEST_CONVERSATION_CONTEXT_MESSAGES,
    TEST_CONVERSATION_ID,
    TEST_FIRST_CHUNK,
    TEST_MAX_MESSAGE_LENGTH,
    TEST_MESSAGE_CREATED_AT,
    TEST_PAGE_TITLE,
    TEST_PREVIOUS_ASSISTANT_MESSAGE,
    TEST_PREVIOUS_USER_MESSAGE,
    TEST_SOURCE_SIMILARITY,
    TEST_SOURCE_URL,
)


def _create_service(
    chunks: list[RetrievedKnowledgeChunk],
    history: list[ConversationMessage] | None = None,
) -> tuple[
    ChatService,
    GeminiGenerationService,
    SemanticRetrievalService,
    ConversationRepository,
]:
    retrieval_service = Mock(spec=SemanticRetrievalService)
    retrieval_service.search = AsyncMock(return_value=chunks)

    generation_service = Mock(spec=GeminiGenerationService)
    generation_service.generate_answer = AsyncMock(return_value=TEST_CHAT_ANSWER)

    conversation_repository = Mock(spec=ConversationRepository)
    conversation_repository.list_recent = AsyncMock(
        return_value=history or [],
    )
    conversation_repository.append_turn = AsyncMock()

    service = ChatService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        conversation_repository=conversation_repository,
        conversation_context_messages=TEST_CONVERSATION_CONTEXT_MESSAGES,
        max_message_length=TEST_MAX_MESSAGE_LENGTH,
    )

    return (
        service,
        generation_service,
        retrieval_service,
        conversation_repository,
    )


def test_answer_returns_grounded_answer_and_sources() -> None:
    history = [
        ConversationMessage(
            conversation_id=TEST_CONVERSATION_ID,
            role=ConversationRole.USER,
            content=TEST_PREVIOUS_USER_MESSAGE,
            created_at=TEST_MESSAGE_CREATED_AT,
        ),
        ConversationMessage(
            conversation_id=TEST_CONVERSATION_ID,
            role=ConversationRole.ASSISTANT,
            content=TEST_PREVIOUS_ASSISTANT_MESSAGE,
            created_at=TEST_MESSAGE_CREATED_AT,
        ),
    ]
    chunks = [
        RetrievedKnowledgeChunk(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=0,
            similarity=TEST_SOURCE_SIMILARITY,
        )
    ]
    service, generation_service, retrieval_service, conversation_repository = (
        _create_service(chunks, history)
    )

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE, TEST_CONVERSATION_ID))

    assert response.conversation_id == TEST_CONVERSATION_ID
    assert response.status == ChatStatus.ANSWERED
    assert response.answer == TEST_CHAT_ANSWER
    assert len(response.sources) == 1
    assert str(response.sources[0].source_url) == TEST_SOURCE_URL
    generation_service.generate_answer.assert_awaited_once_with(
        TEST_CHAT_MESSAGE,
        chunks,
        history,
    )
    expected_history = CHAT_HISTORY_SEPARATOR.join(
        CHAT_HISTORY_ITEM_TEMPLATE.format(
            role=message.role,
            content=message.content,
        )
        for message in history
    )
    retrieval_service.search.assert_awaited_once_with(
        CHAT_RETRIEVAL_QUERY_TEMPLATE.format(
            history=expected_history,
            message=TEST_CHAT_MESSAGE,
        )
    )
    conversation_repository.list_recent.assert_awaited_once_with(
        TEST_CONVERSATION_ID,
        TEST_CONVERSATION_CONTEXT_MESSAGES,
    )
    conversation_repository.append_turn.assert_awaited_once_with(
        TEST_CONVERSATION_ID,
        TEST_CHAT_MESSAGE,
        TEST_CHAT_ANSWER,
    )


def test_answer_uses_human_fallback_without_relevant_context() -> None:
    service, generation_service, _, conversation_repository = _create_service([])

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE, TEST_CONVERSATION_ID))

    assert response.status == ChatStatus.HUMAN_FALLBACK
    assert response.answer == CHAT_INSUFFICIENT_CONTEXT_MESSAGE
    assert response.sources == []
    generation_service.generate_answer.assert_not_awaited()
    conversation_repository.append_turn.assert_awaited_once_with(
        TEST_CONVERSATION_ID,
        TEST_CHAT_MESSAGE,
        CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
    )


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
    service, generation_service, _, _ = _create_service(chunks)
    generation_service.generate_answer.side_effect = AnswerGenerationError()

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE, TEST_CONVERSATION_ID))

    assert response.status == ChatStatus.HUMAN_FALLBACK
    assert response.answer == CHAT_PROVIDER_UNAVAILABLE_MESSAGE
    assert response.sources == []


def test_answer_uses_human_fallback_when_model_requests_it() -> None:
    chunks = [
        RetrievedKnowledgeChunk(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=0,
            similarity=TEST_SOURCE_SIMILARITY,
        )
    ]
    service, generation_service, _, _ = _create_service(chunks)
    generation_service.generate_answer.return_value = CHAT_HUMAN_FALLBACK_MARKER

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE, TEST_CONVERSATION_ID))

    assert response.status == ChatStatus.HUMAN_FALLBACK
    assert response.answer == CHAT_INSUFFICIENT_CONTEXT_MESSAGE
    assert response.sources == []


def test_answer_generates_conversation_id_when_missing() -> None:
    service, _, _, conversation_repository = _create_service([])

    response = asyncio.run(service.answer(TEST_CHAT_MESSAGE))

    stored_conversation_id = conversation_repository.append_turn.await_args.args[0]
    assert response.conversation_id == stored_conversation_id
