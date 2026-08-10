import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import KnowledgeChunkCreate
from app.services.embedding_service import EmbeddingService
from app.services.semantic_retrieval_service import (
    SemanticRetrievalService,
)
from tests.constants import (
    EXPECTED_RETRIEVAL_RESULT_COUNT,
    TEST_DUPLICATE_SOURCE_URL,
    TEST_EMBEDDING_DIMENSION,
    TEST_FIRST_CHUNK,
    TEST_IRRELEVANT_EMBEDDING,
    TEST_MIN_SIMILARITY,
    TEST_MISMATCHED_DIMENSION_CHUNK,
    TEST_PAGE_TITLE,
    TEST_PRIMARY_EMBEDDING,
    TEST_QUERY,
    TEST_RETRIEVAL_TOP_K,
    TEST_SECOND_CHUNK,
    TEST_SOURCE_URL,
    TEST_ZERO_NORM_CHUNK,
)


def test_search_returns_most_relevant_chunk() -> None:
    updated_at = datetime.now(UTC)
    candidates = [
        KnowledgeChunkCreate(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=0,
            updated_at=updated_at,
            embedding=TEST_PRIMARY_EMBEDDING,
        ),
        KnowledgeChunkCreate(
            source_url=TEST_DUPLICATE_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=1,
            updated_at=updated_at,
            embedding=TEST_PRIMARY_EMBEDDING,
        ),
        KnowledgeChunkCreate(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_SECOND_CHUNK,
            chunk_index=2,
            updated_at=updated_at,
            embedding=TEST_IRRELEVANT_EMBEDDING,
        ),
        KnowledgeChunkCreate(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_ZERO_NORM_CHUNK,
            chunk_index=3,
            updated_at=updated_at,
            embedding=[0.0] * TEST_EMBEDDING_DIMENSION,
        ),
        KnowledgeChunkCreate(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_MISMATCHED_DIMENSION_CHUNK,
            chunk_index=4,
            updated_at=updated_at,
            embedding=[*TEST_PRIMARY_EMBEDDING, 0.0],
        ),
    ]

    repository = Mock(spec=KnowledgeRepository)
    repository.list_with_embeddings = AsyncMock(return_value=candidates)

    embedding_service = Mock(spec=EmbeddingService)
    embedding_service.embed_query = AsyncMock(return_value=TEST_PRIMARY_EMBEDDING)

    service = SemanticRetrievalService(
        knowledge_repository=repository,
        embedding_service=embedding_service,
        top_k=TEST_RETRIEVAL_TOP_K,
        min_similarity=TEST_MIN_SIMILARITY,
    )

    results = asyncio.run(service.search(TEST_QUERY))

    assert len(results) == EXPECTED_RETRIEVAL_RESULT_COUNT
    assert results[0].content == TEST_FIRST_CHUNK
    assert results[0].similarity == 1.0
