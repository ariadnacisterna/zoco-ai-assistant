import asyncio
from datetime import UTC, datetime

from app.core.enums import ServiceStatus
from app.core.exceptions import KnowledgeSourceUnavailableError
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import (
    KnowledgeChunkCreate,
    KnowledgeUpdateResponse,
)
from app.services.text_chunking_service import TextChunkingService
from app.services.web_scraper_service import WebScraperService


class KnowledgeService:
    """Coordinate scraping, chunking, and knowledge persistence."""

    def __init__(
        self,
        scraper_service: WebScraperService,
        chunking_service: TextChunkingService,
        knowledge_repository: KnowledgeRepository,
    ) -> None:
        self._scraper_service = scraper_service
        self._chunking_service = chunking_service
        self._knowledge_repository = knowledge_repository
        self._update_lock = asyncio.Lock()

    async def update_knowledge(self) -> KnowledgeUpdateResponse:
        """Update stored knowledge from public sources."""

        async with self._update_lock:
            scraped_pages = await self._scraper_service.scrape()
            updated_at = datetime.now(UTC)

            chunks: list[KnowledgeChunkCreate] = []

            for scraped_page in scraped_pages:
                page_chunks = self._chunking_service.split(scraped_page.content)

                for chunk_index, content in enumerate(page_chunks):
                    chunks.append(
                        KnowledgeChunkCreate(
                            source_url=scraped_page.source_url,
                            title=scraped_page.title,
                            content=content,
                            chunk_index=chunk_index,
                            updated_at=updated_at,
                        )
                    )

            if not chunks:
                raise KnowledgeSourceUnavailableError

            chunks_stored = await self._knowledge_repository.replace_all(chunks)

            return KnowledgeUpdateResponse(
                status=ServiceStatus.OK,
                pages_processed=len(scraped_pages),
                chunks_stored=chunks_stored,
                updated_at=updated_at,
            )
