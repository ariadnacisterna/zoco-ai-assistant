import pytest

from app.services.text_chunking_service import TextChunkingService
from tests.constants import (
    EXPECTED_OVERLAPPING_CHUNKS,
    TEST_BLANK_TEXT,
    TEST_CHUNK_OVERLAP,
    TEST_CHUNK_SIZE,
    TEST_OVERLAPPING_TEXT,
)


def test_split_returns_overlapping_chunks() -> None:
    service = TextChunkingService(
        chunk_size=TEST_CHUNK_SIZE,
        chunk_overlap=TEST_CHUNK_OVERLAP,
    )

    chunks = service.split(TEST_OVERLAPPING_TEXT)

    assert chunks == EXPECTED_OVERLAPPING_CHUNKS


def test_split_returns_empty_list_for_blank_text() -> None:
    service = TextChunkingService(
        chunk_size=TEST_CHUNK_SIZE,
        chunk_overlap=TEST_CHUNK_OVERLAP,
    )

    assert service.split(TEST_BLANK_TEXT) == []


def test_init_raises_when_overlap_is_not_lower_than_chunk_size() -> None:
    with pytest.raises(ValueError):
        TextChunkingService(
            chunk_size=TEST_CHUNK_SIZE,
            chunk_overlap=TEST_CHUNK_SIZE,
        )
