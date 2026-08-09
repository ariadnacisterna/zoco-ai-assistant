from collections.abc import Sequence

from app.core.constants import (
    KNOWLEDGE_COLLECTION_NAME,
    MONGODB_SOURCE_URL_FIELD,
)
from app.database.mongodb import MongoDatabase
from app.schemas.knowledge import KnowledgeChunkCreate


class KnowledgeRepository:
    """Manage knowledge documents stored in MongoDB."""

    def __init__(self, mongo_database: MongoDatabase) -> None:
        self._mongo_database = mongo_database

    async def replace_all(
        self,
        chunks: Sequence[KnowledgeChunkCreate],
    ) -> int:
        """Replace the current knowledge collection with new chunks."""

        collection = self._mongo_database.database[KNOWLEDGE_COLLECTION_NAME]

        documents: list[dict[str, object]] = []

        for chunk in chunks:
            document = chunk.model_dump()
            document[MONGODB_SOURCE_URL_FIELD] = str(chunk.source_url)
            documents.append(document)

        await collection.delete_many({})
        result = await collection.insert_many(documents)

        return len(result.inserted_ids)
