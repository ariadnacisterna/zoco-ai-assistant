import logging
from time import monotonic

from app.core.constants import (
    CHAT_COMPLETED_LOG_MESSAGE,
    CHAT_FALLBACK_INSUFFICIENT_CONTEXT_REASON,
    CHAT_FALLBACK_LOG_MESSAGE,
    CHAT_FALLBACK_PROVIDER_UNAVAILABLE_REASON,
    CHAT_HUMAN_FALLBACK_MARKER,
    CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
    CHAT_MESSAGE_TOO_LONG_MESSAGE,
    CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
)
from app.core.enums import ChatStatus
from app.core.exceptions import (
    AnswerGenerationError,
    ChatMessageTooLongError,
    EmbeddingGenerationError,
)
from app.schemas.chat import ChatResponse, ChatSource
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
        max_message_length: int,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._generation_service = generation_service
        self._max_message_length = max_message_length

    async def answer(self, message: str) -> ChatResponse:
        """Return a grounded answer or a safe human fallback."""

        started_at = monotonic()
        normalized_message = message.strip()

        if len(normalized_message) > self._max_message_length:
            raise ChatMessageTooLongError(CHAT_MESSAGE_TOO_LONG_MESSAGE)

        try:
            chunks = await self._retrieval_service.search(normalized_message)
        except EmbeddingGenerationError:
            return self._fallback(
                message=CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
                reason=CHAT_FALLBACK_PROVIDER_UNAVAILABLE_REASON,
                started_at=started_at,
            )

        if not chunks:
            return self._fallback(
                message=CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
                reason=CHAT_FALLBACK_INSUFFICIENT_CONTEXT_REASON,
                started_at=started_at,
            )

        try:
            answer = await self._generation_service.generate_answer(
                normalized_message,
                chunks,
            )
        except AnswerGenerationError:
            return self._fallback(
                message=CHAT_PROVIDER_UNAVAILABLE_MESSAGE,
                reason=CHAT_FALLBACK_PROVIDER_UNAVAILABLE_REASON,
                started_at=started_at,
            )

        if CHAT_HUMAN_FALLBACK_MARKER in answer:
            return self._fallback(
                message=CHAT_INSUFFICIENT_CONTEXT_MESSAGE,
                reason=CHAT_FALLBACK_INSUFFICIENT_CONTEXT_REASON,
                started_at=started_at,
            )

        response = ChatResponse(
            status=ChatStatus.ANSWERED,
            answer=answer,
            sources=self._build_sources(chunks),
        )
        self._log_completed(response, started_at)

        return response

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
        started_at: float,
    ) -> ChatResponse:
        LOGGER.warning(CHAT_FALLBACK_LOG_MESSAGE, reason)

        response = ChatResponse(
            status=ChatStatus.HUMAN_FALLBACK,
            answer=message,
        )
        ChatService._log_completed(response, started_at)

        return response

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
