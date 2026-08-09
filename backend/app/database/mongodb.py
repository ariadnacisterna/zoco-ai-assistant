from typing import Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings
from app.core.constants import MONGODB_PING_COMMAND

MongoDocument = dict[str, Any]


class MongoDatabase:
    """Manage the MongoDB client and database."""

    def __init__(self, settings: Settings) -> None:
        self._client: AsyncMongoClient[MongoDocument] = AsyncMongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=settings.mongodb_timeout_ms,
        )
        self._database: AsyncDatabase[MongoDocument] = self._client[
            settings.mongodb_database
        ]

    @property
    def database(self) -> AsyncDatabase[MongoDocument]:
        """Return the configured MongoDB database."""

        return self._database

    async def ping(self) -> None:
        """Check whether MongoDB is available."""

        await self._client.admin.command(MONGODB_PING_COMMAND)

    async def close(self) -> None:
        """Close the MongoDB client."""

        await self._client.close()
