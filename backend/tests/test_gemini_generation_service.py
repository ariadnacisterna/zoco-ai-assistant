import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from google.genai import types

from app.core.exceptions import AnswerGenerationError
from app.schemas.knowledge import RetrievedKnowledgeChunk
from app.services.gemini_generation_service import GeminiGenerationService
from tests.constants import (
    TEST_CHAT_MESSAGE,
    TEST_FIRST_CHUNK,
    TEST_GENERATION_MODEL,
    TEST_PAGE_TITLE,
    TEST_SOURCE_SIMILARITY,
    TEST_SOURCE_URL,
)


def test_generate_answer_rejects_empty_provider_response() -> None:
    client = Mock()
    client.aio.models.generate_content = AsyncMock(
        return_value=types.GenerateContentResponse(),
    )
    service = GeminiGenerationService(
        client=client,
        model=TEST_GENERATION_MODEL,
    )
    chunks = [
        RetrievedKnowledgeChunk(
            source_url=TEST_SOURCE_URL,
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
            chunk_index=0,
            similarity=TEST_SOURCE_SIMILARITY,
        )
    ]

    with pytest.raises(AnswerGenerationError):
        asyncio.run(service.generate_answer(TEST_CHAT_MESSAGE, chunks))
