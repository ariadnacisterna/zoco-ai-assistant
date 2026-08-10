import logging
from collections.abc import Sequence

from pydantic import ValidationError

from app.core.constants import (
    INVALID_KNOWLEDGE_DOCUMENTS_LOG_MESSAGE,
    KNOWLEDGE_COLLECTION_NAME,
    MONGODB_EMBEDDING_FIELD,
    MONGODB_ID_FIELD,
    MONGODB_SOURCE_URL_FIELD,
)
from app.database.mongodb import MongoDatabase
from app.schemas.knowledge import KnowledgeChunkCreate

LOGGER = logging.getLogger(__name__)


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

    async def list_with_embeddings(
        self,
    ) -> list[KnowledgeChunkCreate]:
        """Return valid knowledge chunks containing embeddings."""

        collection = self._mongo_database.database[KNOWLEDGE_COLLECTION_NAME]
        cursor = collection.find(
            {
                MONGODB_EMBEDDING_FIELD: {
                    "$exists": True,
                    "$ne": [],
                }
            },
            projection={MONGODB_ID_FIELD: False},
        )

        chunks: list[KnowledgeChunkCreate] = []
        invalid_documents = 0

        async for document in cursor:
            try:
                chunks.append(KnowledgeChunkCreate.model_validate(document))
            except ValidationError:
                invalid_documents += 1

        if invalid_documents:
            LOGGER.warning(
                INVALID_KNOWLEDGE_DOCUMENTS_LOG_MESSAGE,
                invalid_documents,
            )

        return chunks
