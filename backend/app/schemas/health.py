from pydantic import BaseModel

from app.core.enums import DatabaseStatus, KnowledgeStatus, ServiceStatus


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: ServiceStatus
    database: DatabaseStatus
    knowledge: KnowledgeStatus
