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

AUTOMATIC_KNOWLEDGE_UPDATE_ERROR_MESSAGE: str = "Automatic knowledge update failed."
