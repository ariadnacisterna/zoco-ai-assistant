import logging
from collections.abc import Sequence
from time import monotonic
from uuid import UUID, uuid4

from app.core.constants import (
    CHAT_COMPLETED_LOG_MESSAGE,
    CHAT_FALLBACK_INSUFFICIENT_CONTEXT_REASON,
    CHAT_FALLBACK_LOG_MESSAGE,
    CHAT_FALLBACK_PROVIDER_UNAVAILABLE_REASON,
    CHAT_HISTORY_ITEM_TEMPLATE,
    CHAT_HISTORY_SEPARATOR,
    CHAT_HUMAN_FALLBACK_MARKER,
    CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
    CHAT_MESSAGE_TOO_LONG_MESSAGE,
    CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
    CHAT_RETRIEVAL_QUERY_TEMPLATE,
)
from app.core.enums import ChatStatus
from app.core.exceptions import (
    AnswerGenerationError,
    ChatMessageTooLongError,
    EmbeddingGenerationError,
)
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ChatResponse, ChatSource
from app.schemas.conversation import ConversationMessage
from app.schemas.knowledge import RetrievedKnowledgeChunk
from app.services.gemini_generation_service import GeminiGenerationService
from app.services.semantic_retrieval_service import SemanticRetrievalService

LOGGER = logging.getLogger(__name__)


class ChatService:
    """Coordinate retrieval, grounded generation and human fallback."""

    def __init__(
        self,
        retrieval_service: SemanticRetrievalService,
        generation_service: GeminiGenerationService,
        conversation_repository: ConversationRepository,
        conversation_context_messages: int,
        max_message_length: int,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._generation_service = generation_service
        self._conversation_repository = conversation_repository
        self._conversation_context_messages = conversation_context_messages
        self._max_message_length = max_message_length

    async def answer(
        self,
        message: str,
        conversation_id: UUID | None = None,
    ) -> ChatResponse:
        """Return a grounded answer or a safe human fallback."""

        started_at = monotonic()
        normalized_message = message.strip()

        if len(normalized_message) > self._max_message_length:
            raise ChatMessageTooLongError(CHAT_MESSAGE_TOO_LONG_MESSAGE)

        active_conversation_id = conversation_id or uuid4()
        history = await self._conversation_repository.list_recent(
            active_conversation_id,
            self._conversation_context_messages,
        )
        response = await self._create_response(
            normalized_message,
            active_conversation_id,
            history,
        )
        await self._conversation_repository.append_turn(
            active_conversation_id,
            normalized_message,
            response.answer,
        )
        self._log_completed(response, started_at)

        return response

    async def _create_response(
        self,
        message: str,
        conversation_id: UUID,
        history: Sequence[ConversationMessage],
    ) -> ChatResponse:
        retrieval_query = self._build_retrieval_query(history, message)

        try:
            chunks = await self._retrieval_service.search(retrieval_query)
        except EmbeddingGenerationError:
            return self._fallback(
                message=CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
                reason=CHAT_FALLBACK_PROVIDER_UNAVAILABLE_REASON,
                conversation_id=conversation_id,
            )

        if not chunks:
            return self._fallback(
                message=CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
                reason=CHAT_FALLBACK_INSUFFICIENT_CONTEXT_REASON,
                conversation_id=conversation_id,
            )

        try:
            answer = await self._generation_service.generate_answer(
                message,
                chunks,
                history,
            )
        except AnswerGenerationError:
            return self._fallback(
                message=CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
                reason=CHAT_FALLBACK_PROVIDER_UNAVAILABLE_REASON,
                conversation_id=conversation_id,
            )

        if CHAT_HUMAN_FALLBACK_MARKER in answer:
            return self._fallback(
                message=CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
                reason=CHAT_FALLBACK_INSUFFICIENT_CONTEXT_REASON,
                conversation_id=conversation_id,
            )

        return ChatResponse(
            conversation_id=conversation_id,
            status=ChatStatus.ANSWERED,
            answer=answer,
            sources=self._build_sources(chunks),
        )

    async def close(self) -> None:
        """Close resources owned by the generation service."""

        await self._generation_service.close()

    @staticmethod
    def _build_sources(
        chunks: list[RetrievedKnowledgeChunk],
    ) -> list[ChatSource]:
        sources: list[ChatSource] = []
        seen_urls: set[str] = set()

        for chunk in chunks:
            source_url = str(chunk.source_url)

            if source_url in seen_urls:
                continue

            seen_urls.add(source_url)
            sources.append(
                ChatSource(
                    source_url=chunk.source_url,
                    title=chunk.title,
                    similarity=chunk.similarity,
                )
            )

        return sources

    @staticmethod
    def _fallback(
        message: str,
        reason: str,
        conversation_id: UUID,
    ) -> ChatResponse:
        LOGGER.warning(CHAT_FALLBACK_LOG_MESSAGE, reason)

        return ChatResponse(
            conversation_id=conversation_id,
            status=ChatStatus.HUMAN_FALLBACK,
            answer=message,
        )

    @staticmethod
    def _build_retrieval_query(
        history: Sequence[ConversationMessage],
        message: str,
    ) -> str:
        if not history:
            return message

        history_text = CHAT_HISTORY_SEPARATOR.join(
            CHAT_HISTORY_ITEM_TEMPLATE.format(
                role=previous_message.role,
                content=previous_message.content,
            )
            for previous_message in history
        )

        return CHAT_RETRIEVAL_QUERY_TEMPLATE.format(
            history=history_text,
            message=message,
        )

    @staticmethod
    def _log_completed(
        response: ChatResponse,
        started_at: float,
    ) -> None:
        LOGGER.info(
            CHAT_COMPLETED_LOG_MESSAGE,
            response.status,
            len(response.sources),
            monotonic() - started_at,
        )
