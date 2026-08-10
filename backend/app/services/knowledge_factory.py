from google import genai

from app.core.config import Settings
from app.database.mongodb import MongoDatabase
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.services.semantic_retrieval_service import (
    SemanticRetrievalService,
)
from app.services.text_chunking_service import TextChunkingService
from app.services.web_scraper_service import WebScraperService


def create_embedding_service(
    settings: Settings,
) -> EmbeddingService:
    """Create the shared Gemini embedding service."""

    client = genai.Client(
        api_key=settings.gemini_api_key.get_secret_value(),
    )

    return EmbeddingService(
        client=client,
        model=settings.gemini_embedding_model,
        dimension=settings.embedding_dimension,
    )


def create_knowledge_service(
    settings: Settings,
    mongo_database: MongoDatabase,
    embedding_service: EmbeddingService,
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
        embedding_service=embedding_service,
        knowledge_repository=knowledge_repository,
    )


def create_semantic_retrieval_service(
    settings: Settings,
    mongo_database: MongoDatabase,
    embedding_service: EmbeddingService,
) -> SemanticRetrievalService:
    """Create the semantic retrieval service."""

    knowledge_repository = KnowledgeRepository(mongo_database)

    return SemanticRetrievalService(
        knowledge_repository=knowledge_repository,
        embedding_service=embedding_service,
        top_k=settings.retrieval_top_k,
        min_similarity=settings.min_similarity,
    )
