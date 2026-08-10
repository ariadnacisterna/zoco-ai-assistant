import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from google.genai import types

from app.core.constants import (
    EMBEDDING_DOCUMENT_TEMPLATE,
    EMBEDDING_QUERY_TEMPLATE,
    EMPTY_RETRIEVAL_QUERY_MESSAGE,
)
from app.core.exceptions import EmbeddingGenerationError
from app.services.embedding_service import EmbeddingService
from tests.constants import (
    TEST_EMBEDDING_DIMENSION,
    TEST_EMBEDDING_MODEL,
    TEST_FIRST_CHUNK,
    TEST_PAGE_TITLE,
    TEST_PRIMARY_EMBEDDING,
    TEST_QUERY,
    TEST_SECOND_CHUNK,
    TEST_SECONDARY_EMBEDDING,
)


def test_embed_documents_returns_one_vector_per_document() -> None:
    client = Mock()
    client.aio.models.embed_content = AsyncMock(
        return_value=types.EmbedContentResponse(
            embeddings=[
                types.ContentEmbedding(values=TEST_PRIMARY_EMBEDDING),
                types.ContentEmbedding(values=TEST_SECONDARY_EMBEDDING),
            ]
        )
    )
    service = EmbeddingService(
        client=client,
        model=TEST_EMBEDDING_MODEL,
        dimension=TEST_EMBEDDING_DIMENSION,
    )

    result = asyncio.run(
        service.embed_documents(
            [
                (TEST_PAGE_TITLE, TEST_FIRST_CHUNK),
                (TEST_PAGE_TITLE, TEST_SECOND_CHUNK),
            ]
        )
    )

    assert result == [
        TEST_PRIMARY_EMBEDDING,
        TEST_SECONDARY_EMBEDDING,
    ]

    contents = client.aio.models.embed_content.await_args.kwargs["contents"]
    assert len(contents) == len(result)
    assert contents[0].parts[0].text == (
        EMBEDDING_DOCUMENT_TEMPLATE.format(
            title=TEST_PAGE_TITLE,
            content=TEST_FIRST_CHUNK,
        )
    )


def test_embed_query_uses_retrieval_query_format() -> None:
    client = Mock()
    client.aio.models.embed_content = AsyncMock(
        return_value=types.EmbedContentResponse(
            embeddings=[types.ContentEmbedding(values=TEST_PRIMARY_EMBEDDING)]
        )
    )
    service = EmbeddingService(
        client=client,
        model=TEST_EMBEDDING_MODEL,
        dimension=TEST_EMBEDDING_DIMENSION,
    )

    result = asyncio.run(service.embed_query(TEST_QUERY))

    assert result == TEST_PRIMARY_EMBEDDING

    contents = client.aio.models.embed_content.await_args.kwargs["contents"]
    assert contents[0].parts[0].text == (
        EMBEDDING_QUERY_TEMPLATE.format(query=TEST_QUERY)
    )


def test_embed_query_rejects_empty_query() -> None:
    client = Mock()
    client.aio.models.embed_content = AsyncMock()
    service = EmbeddingService(
        client=client,
        model=TEST_EMBEDDING_MODEL,
        dimension=TEST_EMBEDDING_DIMENSION,
    )

    with pytest.raises(
        ValueError,
        match=EMPTY_RETRIEVAL_QUERY_MESSAGE,
    ):
        asyncio.run(service.embed_query("  \n  "))

    client.aio.models.embed_content.assert_not_awaited()


def test_embed_query_rejects_invalid_provider_response() -> None:
    invalid_responses = [
        types.EmbedContentResponse(embeddings=[]),
        types.EmbedContentResponse(
            embeddings=[
                types.ContentEmbedding(
                    values=TEST_PRIMARY_EMBEDDING[:-1],
                )
            ]
        ),
    ]

    for invalid_response in invalid_responses:
        client = Mock()
        client.aio.models.embed_content = AsyncMock(return_value=invalid_response)
        service = EmbeddingService(
            client=client,
            model=TEST_EMBEDDING_MODEL,
            dimension=TEST_EMBEDDING_DIMENSION,
        )

        with pytest.raises(EmbeddingGenerationError):
            asyncio.run(service.embed_query(TEST_QUERY))
