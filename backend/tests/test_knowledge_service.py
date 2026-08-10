import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.enums import ServiceStatus
from app.core.exceptions import KnowledgeSourceUnavailableError
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import ScrapedPage
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.services.text_chunking_service import TextChunkingService
from app.services.web_scraper_service import WebScraperService
from tests.constants import (
    TEST_FIRST_CHUNK,
    TEST_PAGE_CONTENT,
    TEST_PAGE_TITLE,
    TEST_PRIMARY_EMBEDDING,
    TEST_SECOND_CHUNK,
    TEST_SECONDARY_EMBEDDING,
    TEST_SOURCE_URL,
)


def test_update_knowledge_stores_generated_embeddings() -> None:
    scraper_service = Mock(spec=WebScraperService)
    scraper_service.scrape = AsyncMock(
        return_value=[
            ScrapedPage(
                source_url=TEST_SOURCE_URL,
                title=TEST_PAGE_TITLE,
                content=TEST_PAGE_CONTENT,
            )
        ]
    )

    chunking_service = Mock(spec=TextChunkingService)
    chunking_service.split.return_value = [
        TEST_FIRST_CHUNK,
        TEST_SECOND_CHUNK,
    ]

    embedding_service = Mock(spec=EmbeddingService)
    embedding_service.embed_documents = AsyncMock(
        return_value=[
            TEST_PRIMARY_EMBEDDING,
            TEST_SECONDARY_EMBEDDING,
        ]
    )

    knowledge_repository = Mock(spec=KnowledgeRepository)
    knowledge_repository.replace_all = AsyncMock(return_value=2)

    service = KnowledgeService(
        scraper_service=scraper_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        knowledge_repository=knowledge_repository,
    )

    response = asyncio.run(service.update_knowledge())

    assert response.status == ServiceStatus.OK
    assert response.pages_processed == 1
    assert response.chunks_stored == 2

    embedding_service.embed_documents.assert_awaited_once_with(
        [
            (TEST_PAGE_TITLE, TEST_FIRST_CHUNK),
            (TEST_PAGE_TITLE, TEST_SECOND_CHUNK),
        ]
    )

    stored_chunks = knowledge_repository.replace_all.await_args.args[0]

    assert stored_chunks[0].embedding == TEST_PRIMARY_EMBEDDING
    assert stored_chunks[1].embedding == TEST_SECONDARY_EMBEDDING


def test_update_knowledge_without_chunks_skips_embeddings() -> None:
    scraper_service = Mock(spec=WebScraperService)
    scraper_service.scrape = AsyncMock(
        return_value=[
            ScrapedPage(
                source_url=TEST_SOURCE_URL,
                title=TEST_PAGE_TITLE,
                content=TEST_PAGE_CONTENT,
            )
        ]
    )

    chunking_service = Mock(spec=TextChunkingService)
    chunking_service.split.return_value = []

    embedding_service = Mock(spec=EmbeddingService)
    embedding_service.embed_documents = AsyncMock()

    knowledge_repository = Mock(spec=KnowledgeRepository)
    knowledge_repository.replace_all = AsyncMock()

    service = KnowledgeService(
        scraper_service=scraper_service,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        knowledge_repository=knowledge_repository,
    )

    with pytest.raises(KnowledgeSourceUnavailableError):
        asyncio.run(service.update_knowledge())

    embedding_service.embed_documents.assert_not_awaited()
    knowledge_repository.replace_all.assert_not_awaited()
