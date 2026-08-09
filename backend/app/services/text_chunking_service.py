from app.core.constants import INVALID_CHUNK_CONFIGURATION_MESSAGE


class TextChunkingService:
    """Split text into overlapping character chunks."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(INVALID_CHUNK_CONFIGURATION_MESSAGE)

        self._chunk_size = chunk_size
        self._chunk_step = chunk_size - chunk_overlap

    def split(self, text: str) -> list[str]:
        """Split normalized text into overlapping chunks."""

        normalized_text = " ".join(text.split())

        if not normalized_text:
            return []

        chunks: list[str] = []
        start = 0

        while start < len(normalized_text):
            end = min(start + self._chunk_size, len(normalized_text))
            chunk = normalized_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(normalized_text):
                break

            start += self._chunk_step

        return chunks
