import asyncio
import logging
from datetime import UTC, datetime
from time import perf_counter

from app.core.constants import (
    KNOWLEDGE_UPDATE_COMPLETED_LOG_MESSAGE,
    KNOWLEDGE_UPDATE_STARTED_LOG_MESSAGE,
)
from app.core.enums import ServiceStatus
from app.core.exceptions import KnowledgeSourceUnavailableError
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import (
    KnowledgeChunkCreate,
    KnowledgeUpdateResponse,
    ScrapedPage,
)
from app.services.embedding_service import EmbeddingService
from app.services.text_chunking_service import TextChunkingService
from app.services.web_scraper_service import WebScraperService

LOGGER = logging.getLogger(__name__)


class KnowledgeService:
    """Coordinate scraping, embedding, and knowledge persistence."""

    def __init__(
        self,
        scraper_service: WebScraperService,
        chunking_service: TextChunkingService,
        embedding_service: EmbeddingService,
        knowledge_repository: KnowledgeRepository,
    ) -> None:
        self._scraper_service = scraper_service
        self._chunking_service = chunking_service
        self._embedding_service = embedding_service
        self._knowledge_repository = knowledge_repository
        self._update_lock = asyncio.Lock()

    async def update_knowledge(self) -> KnowledgeUpdateResponse:
        """Update stored knowledge from public sources."""

        async with self._update_lock:
            started_at = perf_counter()
            LOGGER.info(KNOWLEDGE_UPDATE_STARTED_LOG_MESSAGE)

            scraped_pages = await self._scraper_service.scrape()
            chunk_data: list[tuple[ScrapedPage, int, str]] = []

            for scraped_page in scraped_pages:
                page_chunks = self._chunking_service.split(scraped_page.content)

                for chunk_index, content in enumerate(page_chunks):
                    chunk_data.append((scraped_page, chunk_index, content))

            if not chunk_data:
                raise KnowledgeSourceUnavailableError

            embedding_inputs = [
                (scraped_page.title, content) for scraped_page, _, content in chunk_data
            ]
            embeddings = await self._embedding_service.embed_documents(embedding_inputs)
            updated_at = datetime.now(UTC)

            chunks = [
                KnowledgeChunkCreate(
                    source_url=scraped_page.source_url,
                    title=scraped_page.title,
                    content=content,
                    chunk_index=chunk_index,
                    updated_at=updated_at,
                    embedding=embedding,
                )
                for (
                    scraped_page,
                    chunk_index,
                    content,
                ), embedding in zip(
                    chunk_data,
                    embeddings,
                    strict=True,
                )
            ]

            chunks_stored = await self._knowledge_repository.replace_all(chunks)

            LOGGER.info(
                KNOWLEDGE_UPDATE_COMPLETED_LOG_MESSAGE,
                len(scraped_pages),
                chunks_stored,
                perf_counter() - started_at,
            )

            return KnowledgeUpdateResponse(
                status=ServiceStatus.OK,
                pages_processed=len(scraped_pages),
                chunks_stored=chunks_stored,
                updated_at=updated_at,
            )
