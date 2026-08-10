import logging
from time import monotonic

import httpx
from google import genai
from google.genai import errors, types

from app.core.constants import (
    CHAT_CONTEXT_ITEM_TEMPLATE,
    CHAT_CONTEXT_SEPARATOR,
    CHAT_GENERATION_TEMPERATURE,
    CHAT_SYSTEM_INSTRUCTION,
    CHAT_USER_PROMPT_TEMPLATE,
    GENERATION_COMPLETED_LOG_MESSAGE,
    GENERATION_FAILED_LOG_MESSAGE,
    GENERATION_STARTED_LOG_MESSAGE,
    INVALID_GENERATION_RESPONSE_LOG_MESSAGE,
    INVALID_GENERATION_RESPONSE_MESSAGE,
)
from app.core.exceptions import AnswerGenerationError
from app.schemas.knowledge import RetrievedKnowledgeChunk

LOGGER = logging.getLogger(__name__)


class GeminiGenerationService:
    """Generate answers from retrieved ZOCO knowledge."""

    def __init__(
        self,
        client: genai.Client,
        model: str,
    ) -> None:
        self._client = client
        self._model = model

    async def generate_answer(
        self,
        question: str,
        chunks: list[RetrievedKnowledgeChunk],
    ) -> str:
        """Generate one answer grounded in the supplied chunks."""

        started_at = monotonic()
        context = CHAT_CONTEXT_SEPARATOR.join(
            CHAT_CONTEXT_ITEM_TEMPLATE.format(
                title=chunk.title,
                source_url=chunk.source_url,
                content=chunk.content,
            )
            for chunk in chunks
        )
        prompt = CHAT_USER_PROMPT_TEMPLATE.format(
            question=question,
            context=context,
        )

        LOGGER.info(GENERATION_STARTED_LOG_MESSAGE, len(chunks))

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=CHAT_SYSTEM_INSTRUCTION,
                    temperature=CHAT_GENERATION_TEMPERATURE,
                ),
            )
        except (errors.APIError, httpx.HTTPError) as error:
            LOGGER.exception(GENERATION_FAILED_LOG_MESSAGE)
            raise AnswerGenerationError from error

        answer = response.text.strip() if response.text else ""

        if not answer:
            LOGGER.error(INVALID_GENERATION_RESPONSE_LOG_MESSAGE)
            raise AnswerGenerationError(INVALID_GENERATION_RESPONSE_MESSAGE)

        LOGGER.info(
            GENERATION_COMPLETED_LOG_MESSAGE,
            monotonic() - started_at,
        )

        return answer

    async def close(self) -> None:
        """Close Gemini HTTP resources."""

        await self._client.aio.aclose()
        self._client.close()
