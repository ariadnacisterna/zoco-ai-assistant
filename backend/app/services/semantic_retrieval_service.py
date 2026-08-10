import logging
from math import sqrt
from typing import Final

from app.core.constants import (
    INVALID_EMBEDDING_VECTOR_LOG_MESSAGE,
    SEMANTIC_RETRIEVAL_COMPLETED_LOG_MESSAGE,
)
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import RetrievedKnowledgeChunk
from app.services.embedding_service import EmbeddingService

LOGGER = logging.getLogger(__name__)

ZERO_NORM: Final[float] = 0.0


class SemanticRetrievalService:
    """Retrieve knowledge chunks by semantic similarity."""

    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
        embedding_service: EmbeddingService,
        top_k: int,
        min_similarity: float,
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._embedding_service = embedding_service
        self._top_k = top_k
        self._min_similarity = min_similarity

    async def search(self, query: str) -> list[RetrievedKnowledgeChunk]:
        """Return the most relevant chunks for a query."""

        candidates = await self._knowledge_repository.list_with_embeddings()

        if not candidates:
            self._log_result(
                candidates_count=0,
                results=[],
            )
            return []

        query_embedding = await self._embedding_service.embed_query(query)
        ranked_chunks: list[RetrievedKnowledgeChunk] = []

        for candidate in candidates:
            similarity = self._cosine_similarity(
                query_embedding,
                candidate.embedding,
            )

            if similarity is None:
                LOGGER.warning(INVALID_EMBEDDING_VECTOR_LOG_MESSAGE)
                continue

            if similarity < self._min_similarity:
                continue

            ranked_chunks.append(
                RetrievedKnowledgeChunk(
                    source_url=candidate.source_url,
                    title=candidate.title,
                    content=candidate.content,
                    chunk_index=candidate.chunk_index,
                    similarity=similarity,
                )
            )

        ranked_chunks.sort(
            key=lambda chunk: chunk.similarity,
            reverse=True,
        )
        results: list[RetrievedKnowledgeChunk] = []
        seen_content_keys: set[str] = set()

        for ranked_chunk in ranked_chunks:
            content_key = self._content_key(ranked_chunk.content)

            if content_key in seen_content_keys:
                continue

            seen_content_keys.add(content_key)
            results.append(ranked_chunk)

            if len(results) == self._top_k:
                break

        self._log_result(
            candidates_count=len(candidates),
            results=results,
        )

        return results

    @staticmethod
    def _cosine_similarity(
        first_embedding: list[float],
        second_embedding: list[float],
    ) -> float | None:
        if not first_embedding or len(first_embedding) != len(second_embedding):
            return None

        dot_product = sum(
            first_value * second_value
            for first_value, second_value in zip(
                first_embedding,
                second_embedding,
                strict=True,
            )
        )
        first_norm = sqrt(sum(value * value for value in first_embedding))
        second_norm = sqrt(sum(value * value for value in second_embedding))

        if first_norm == ZERO_NORM or second_norm == ZERO_NORM:
            return None

        return dot_product / (first_norm * second_norm)

    @staticmethod
    def _content_key(content: str) -> str:
        """Build a normalized key used to detect duplicate content."""

        return "".join(
            character for character in content.casefold() if character.isalnum()
        )

    @staticmethod
    def _log_result(
        candidates_count: int,
        results: list[RetrievedKnowledgeChunk],
    ) -> None:
        best_score = results[0].similarity if results else None

        LOGGER.info(
            SEMANTIC_RETRIEVAL_COMPLETED_LOG_MESSAGE,
            candidates_count,
            len(results),
            best_score,
        )
