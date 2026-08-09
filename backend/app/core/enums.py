from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class ServiceStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


class DatabaseStatus(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class KnowledgeStatus(StrEnum):
    READY = "ready"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"
