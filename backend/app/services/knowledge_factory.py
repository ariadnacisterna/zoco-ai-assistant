from app.core.config import Settings
from app.database.mongodb import MongoDatabase
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_service import KnowledgeService
from app.services.text_chunking_service import TextChunkingService
from app.services.web_scraper_service import WebScraperService


def create_knowledge_service(
    settings: Settings,
    mongo_database: MongoDatabase,
) -> KnowledgeService:
    """Create the knowledge service and its dependencies."""

    scraper_service = WebScraperService(
        base_url=settings.zoco_base_url,
        max_pages=settings.max_crawl_pages,
        timeout_ms=settings.scraper_timeout_ms,
    )

    chunking_service = TextChunkingService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    knowledge_repository = KnowledgeRepository(mongo_database)

    return KnowledgeService(
        scraper_service=scraper_service,
        chunking_service=chunking_service,
        knowledge_repository=knowledge_repository,
    )
