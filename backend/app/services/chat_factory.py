from google import genai

from app.core.config import Settings
from app.services.chat_service import ChatService
from app.services.gemini_generation_service import GeminiGenerationService
from app.services.semantic_retrieval_service import SemanticRetrievalService


def create_chat_service(
    settings: Settings,
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

    return ChatService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        max_message_length=settings.max_message_length,
    )
