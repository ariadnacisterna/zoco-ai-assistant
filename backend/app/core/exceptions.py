class KnowledgeSourceUnavailableError(Exception):
    """Raised when public knowledge cannot be obtained."""


class EmbeddingGenerationError(Exception):
    """Raised when Gemini cannot generate valid embeddings."""


class AnswerGenerationError(Exception):
    """Raised when Gemini cannot generate a valid grounded answer."""


class ChatMessageTooLongError(ValueError):
    """Raised when a chat message exceeds the configured limit."""
