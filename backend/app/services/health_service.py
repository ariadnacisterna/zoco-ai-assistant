from pymongo.errors import PyMongoError

from app.core.enums import DatabaseStatus, KnowledgeStatus, ServiceStatus
from app.repositories.health_repository import HealthRepository
from app.schemas.health import HealthResponse


class HealthService:
    """Build the application health status."""

    def __init__(self, health_repository: HealthRepository) -> None:
        self._health_repository = health_repository

    async def get_health_status(self) -> HealthResponse:
        """Return the service, database, and knowledge statuses."""

        try:
            await self._health_repository.check_connection()
            has_knowledge = await self._health_repository.has_knowledge()

            if has_knowledge:
                knowledge_status = KnowledgeStatus.READY
            else:
                knowledge_status = KnowledgeStatus.EMPTY

            return HealthResponse(
                status=ServiceStatus.OK,
                database=DatabaseStatus.CONNECTED,
                knowledge=knowledge_status,
            )
        except PyMongoError:
            return HealthResponse(
                status=ServiceStatus.ERROR,
                database=DatabaseStatus.DISCONNECTED,
                knowledge=KnowledgeStatus.UNAVAILABLE,
            )
