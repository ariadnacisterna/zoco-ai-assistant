from app.services.text_chunking_service import TextChunkingService


def test_split_returns_overlapping_chunks() -> None:
    service = TextChunkingService(
        chunk_size=10,
        chunk_overlap=2,
    )

    chunks = service.split("abcdefghijklmnopqrstuvw")

    assert chunks == [
        "abcdefghij",
        "ijklmnopqr",
        "qrstuvw",
    ]


def test_split_returns_empty_list_for_blank_text() -> None:
    service = TextChunkingService(
        chunk_size=10,
        chunk_overlap=2,
    )

    assert service.split("   ") == []
