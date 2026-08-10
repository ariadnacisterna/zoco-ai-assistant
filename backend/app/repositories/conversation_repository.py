from datetime import UTC, datetime
from uuid import UUID

from pymongo import DESCENDING

from app.core.constants import (
    CONVERSATION_COLLECTION_NAME,
    MONGODB_CONVERSATION_ID_FIELD,
    MONGODB_ID_FIELD,
)
from app.core.enums import ConversationRole
from app.database.mongodb import MongoDatabase
from app.schemas.conversation import ConversationMessage


class ConversationRepository:
    """Manage conversation messages stored in MongoDB."""

    def __init__(self, mongo_database: MongoDatabase) -> None:
        self._mongo_database = mongo_database

    async def list_recent(
        self,
        conversation_id: UUID,
        limit: int,
    ) -> list[ConversationMessage]:
        """Return the latest messages in chronological order."""

        collection = self._mongo_database.database[CONVERSATION_COLLECTION_NAME]
        cursor = (
            collection.find(
                {
                    MONGODB_CONVERSATION_ID_FIELD: str(conversation_id),
                },
                projection={MONGODB_ID_FIELD: False},
            )
            .sort(MONGODB_ID_FIELD, DESCENDING)
            .limit(limit)
        )

        messages = [
            ConversationMessage.model_validate(document) async for document in cursor
        ]
        messages.reverse()

        return messages

    async def append_turn(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
    ) -> None:
        """Store one complete user and assistant turn."""

        created_at = datetime.now(UTC)
        messages = (
            ConversationMessage(
                conversation_id=conversation_id,
                role=ConversationRole.USER,
                content=user_message,
                created_at=created_at,
            ),
            ConversationMessage(
                conversation_id=conversation_id,
                role=ConversationRole.ASSISTANT,
                content=assistant_message,
                created_at=created_at,
            ),
        )
        documents: list[dict[str, object]] = []

        for message in messages:
            document = message.model_dump()
            document[MONGODB_CONVERSATION_ID_FIELD] = str(message.conversation_id)
            documents.append(document)

        collection = self._mongo_database.database[CONVERSATION_COLLECTION_NAME]
        await collection.insert_many(documents)
