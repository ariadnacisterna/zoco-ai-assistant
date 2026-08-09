APP_NAME: str = "ZOCO AI Assistant"
APP_DESCRIPTION: str = "REST API for the ZOCO Pagos conversational assistant"
APP_VERSION: str = "0.1.0"
API_PREFIX: str = "/api"
HEALTH_PATH: str = "/health"
HEALTH_TAG: str = "health"

CORS_ALLOWED_METHODS: tuple[str, ...] = ("GET", "POST")
CORS_ALLOWED_HEADERS: tuple[str, ...] = ("Content-Type",)

DOCS_PATH: str = "/docs"
