import logging
from collections.abc import Sequence

import httpx
from google import genai
from google.genai import errors, types

from app.core.constants import (
    EMBEDDING_DOCUMENT_TEMPLATE,
    EMBEDDING_GENERATION_COMPLETED_LOG_MESSAGE,
    EMBEDDING_GENERATION_FAILED_LOG_MESSAGE,
    EMBEDDING_GENERATION_STARTED_LOG_MESSAGE,
    EMBEDDING_QUERY_TEMPLATE,
    EMPTY_RETRIEVAL_QUERY_MESSAGE,
    INVALID_EMBEDDING_RESPONSE_LOG_MESSAGE,
    INVALID_EMBEDDING_RESPONSE_MESSAGE,
)
from app.core.exceptions import EmbeddingGenerationError

LOGGER = logging.getLogger(__name__)


class EmbeddingService:
    """Generate document and query embeddings with Gemini."""

    def __init__(
        self,
        client: genai.Client,
        model: str,
        dimension: int,
    ) -> None:
        self._client = client
        self._model = model
        self._dimension = dimension

    async def embed_documents(
        self,
        documents: Sequence[tuple[str, str]],
    ) -> list[list[float]]:
        """Generate one embedding for every title and content pair."""

        formatted_documents = [
            EMBEDDING_DOCUMENT_TEMPLATE.format(
                title=title.strip(),
                content=content.strip(),
            )
            for title, content in documents
        ]

        return await self._embed(formatted_documents)

    async def embed_query(self, query: str) -> list[float]:
        """Generate an embedding optimized for semantic search."""

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError(EMPTY_RETRIEVAL_QUERY_MESSAGE)

        formatted_query = EMBEDDING_QUERY_TEMPLATE.format(
            query=normalized_query,
        )

        embeddings = await self._embed([formatted_query])

        return embeddings[0]

    async def close(self) -> None:
        """Close Gemini HTTP resources."""

        await self._client.aio.aclose()
        self._client.close()

    async def _embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        contents = [types.Content(parts=[types.Part(text=text)]) for text in texts]

        LOGGER.info(
            EMBEDDING_GENERATION_STARTED_LOG_MESSAGE,
            len(contents),
        )

        try:
            response = await self._client.aio.models.embed_content(
                model=self._model,
                contents=contents,
                config=types.EmbedContentConfig(
                    output_dimensionality=self._dimension,
                ),
            )
        except (errors.APIError, httpx.HTTPError) as error:
            LOGGER.exception(EMBEDDING_GENERATION_FAILED_LOG_MESSAGE)
            raise EmbeddingGenerationError from error

        response_embeddings = response.embeddings

        if response_embeddings is None or len(response_embeddings) != len(contents):
            received_count = (
                len(response_embeddings) if response_embeddings is not None else 0
            )
            LOGGER.error(
                INVALID_EMBEDDING_RESPONSE_LOG_MESSAGE,
                received_count,
                len(contents),
            )
            raise EmbeddingGenerationError(
                INVALID_EMBEDDING_RESPONSE_MESSAGE,
            )

        embeddings: list[list[float]] = []

        for response_embedding in response_embeddings:
            values = response_embedding.values

            if values is None or len(values) != self._dimension:
                LOGGER.error(
                    INVALID_EMBEDDING_RESPONSE_LOG_MESSAGE,
                    0 if values is None else len(values),
                    self._dimension,
                )
                raise EmbeddingGenerationError(
                    INVALID_EMBEDDING_RESPONSE_MESSAGE,
                )

            embeddings.append(list(values))

        LOGGER.info(
            EMBEDDING_GENERATION_COMPLETED_LOG_MESSAGE,
            len(embeddings),
        )

        return embeddings
