from app.core.constants import (
    KNOWLEDGE_COLLECTION_NAME,
    MONGODB_EMBEDDING_FIELD,
    MONGODB_ID_FIELD,
)
from app.database.mongodb import MongoDatabase


class HealthRepository:
    def __init__(self, database: MongoDatabase) -> None:
        self._mongo_database = database

    async def check_connection(self) -> None:
        """Check if the MongoDB connection is alive."""

        await self._mongo_database.ping()

    async def has_knowledge(self) -> bool:
        """Check if the knowledge collection has any documents."""

        collection = self._mongo_database.database[KNOWLEDGE_COLLECTION_NAME]
        document = await collection.find_one(
            {
                MONGODB_EMBEDDING_FIELD: {
                    "$exists": True,
                    "$ne": [],
                }
            },
            projection=[MONGODB_ID_FIELD],
        )

        return document is not None
