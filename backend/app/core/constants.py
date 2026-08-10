APP_NAME: str = "ZOCO AI Assistant"
APP_DESCRIPTION: str = "REST API for the ZOCO Pagos conversational assistant"
APP_VERSION: str = "0.1.0"
API_PREFIX: str = "/api"
HEALTH_PATH: str = "/health"
HEALTH_TAG: str = "health"

CORS_ALLOWED_METHODS: tuple[str, ...] = ("GET", "POST", "PUT")
CORS_ALLOWED_HEADERS: tuple[str, ...] = ("Content-Type",)

DOCS_PATH: str = "/docs"


MONGODB_PING_COMMAND: str = "ping"
MONGODB_ID_FIELD: str = "_id"

KNOWLEDGE_COLLECTION_NAME: str = "knowledge_chunks"

KNOWLEDGE_PATH: str = "/knowledge"
KNOWLEDGE_TAG: str = "knowledge"

KNOWLEDGE_SOURCE_UNAVAILABLE_MESSAGE: str = (
    "The public knowledge source is unavailable."
)
DATABASE_UNAVAILABLE_MESSAGE: str = "The database is unavailable."

MONGODB_SOURCE_URL_FIELD: str = "source_url"

HTML_PARSER: str = "html.parser"
HTML_MAIN_SELECTOR: str = "main"
HTML_LINK_SELECTOR: str = "a[href]"
HTML_IGNORED_SELECTOR: str = "script, style, noscript, svg"
HTML_TEXT_SEPARATOR: str = " "
SCRAPER_WAIT_UNTIL: str = "domcontentloaded"
ALLOWED_URL_SCHEMES: tuple[str, ...] = ("http", "https")

INVALID_CHUNK_CONFIGURATION_MESSAGE: str = (
    "CHUNK_SIZE must be positive and CHUNK_OVERLAP must be non-negative "
    "and lower than CHUNK_SIZE."
)

AUTOMATIC_KNOWLEDGE_UPDATE_ERROR_MESSAGE: str = "Automatic knowledge update failed."

MONGODB_EMBEDDING_FIELD: str = "embedding"

EMBEDDING_DOCUMENT_TEMPLATE: str = "title: {title} | text: {content}"
EMBEDDING_QUERY_TEMPLATE: str = "task: search result | query: {query}"

EMPTY_RETRIEVAL_QUERY_MESSAGE: str = "The retrieval query cannot be empty."
INVALID_EMBEDDING_RESPONSE_MESSAGE: str = (
    "Gemini returned an invalid embedding response."
)
EMBEDDING_PROVIDER_UNAVAILABLE_MESSAGE: str = "The embedding provider is unavailable."

KNOWLEDGE_UPDATE_STARTED_LOG_MESSAGE: str = "Knowledge update started."
KNOWLEDGE_UPDATE_COMPLETED_LOG_MESSAGE: str = (
    "Knowledge update completed: pages=%s chunks=%s elapsed_seconds=%.3f."
)
EMBEDDING_GENERATION_STARTED_LOG_MESSAGE: str = (
    "Embedding generation started: items=%s."
)
EMBEDDING_GENERATION_COMPLETED_LOG_MESSAGE: str = (
    "Embedding generation completed: items=%s."
)
EMBEDDING_GENERATION_FAILED_LOG_MESSAGE: str = "Gemini embedding generation failed."
INVALID_EMBEDDING_RESPONSE_LOG_MESSAGE: str = (
    "Gemini returned %s embeddings; expected %s."
)
INVALID_KNOWLEDGE_DOCUMENTS_LOG_MESSAGE: str = (
    "Ignored invalid knowledge documents: count=%s."
)
INVALID_EMBEDDING_VECTOR_LOG_MESSAGE: str = (
    "Ignored knowledge chunk with an incompatible embedding."
)
SEMANTIC_RETRIEVAL_COMPLETED_LOG_MESSAGE: str = (
    "Semantic retrieval completed: candidates=%s selected=%s best_score=%s."
)

APPLICATION_LOGGER_NAME: str = "app"
UVICORN_LOGGER_NAME: str = "uvicorn"
