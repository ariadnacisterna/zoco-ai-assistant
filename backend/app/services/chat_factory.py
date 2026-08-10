from google import genai

from app.core.config import Settings
from app.database.mongodb import MongoDatabase
from app.repositories.conversation_repository import ConversationRepository
from app.services.chat_service import ChatService
from app.services.gemini_generation_service import GeminiGenerationService
from app.services.semantic_retrieval_service import SemanticRetrievalService


def create_chat_service(
    settings: Settings,
    mongo_database: MongoDatabase,
    retrieval_service: SemanticRetrievalService,
) -> ChatService:
    """Create the shared chat service and its dependencies."""

    client = genai.Client(
        api_key=settings.gemini_api_key.get_secret_value(),
    )
    generation_service = GeminiGenerationService(
        client=client,
        model=settings.gemini_generation_model,
    )
    conversation_repository = ConversationRepository(mongo_database)

    return ChatService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        conversation_repository=conversation_repository,
        conversation_context_messages=settings.conversation_context_messages,
        max_message_length=settings.max_message_length,
    )
