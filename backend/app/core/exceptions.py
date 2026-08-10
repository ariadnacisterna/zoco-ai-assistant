class KnowledgeSourceUnavailableError(Exception):
    """Raised when public knowledge cannot be obtained."""


class EmbeddingGenerationError(Exception):
    """Raised when Gemini cannot generate valid embeddings."""
