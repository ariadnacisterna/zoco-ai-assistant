from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class ServiceStatus(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"


class DatabaseStatus(StrEnum):
    CONNECTED = "connected"
    UNAVAILABLE = "unavailable"


class KnowledgeStatus(StrEnum):
    READY = "ready"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"
