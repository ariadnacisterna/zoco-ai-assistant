import asyncio
from unittest.mock import AsyncMock, MagicMock

from pymongo import DESCENDING

from app.core.constants import (
    CONVERSATION_COLLECTION_NAME,
    MONGODB_CONVERSATION_ID_FIELD,
    MONGODB_ID_FIELD,
)
from app.core.enums import ConversationRole
from app.database.mongodb import MongoDatabase
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import ConversationMessage
from tests.constants import (
    EXPECTED_CONVERSATION_MESSAGE_COUNT,
    TEST_CHAT_ANSWER,
    TEST_CHAT_MESSAGE,
    TEST_CONVERSATION_CONTEXT_MESSAGES,
    TEST_CONVERSATION_ID,
    TEST_MESSAGE_CREATED_AT,
)


def _create_repository(
    collection: MagicMock,
) -> tuple[ConversationRepository, MagicMock]:
    mongo_database = MagicMock(spec=MongoDatabase)
    database = MagicMock()
    database.__getitem__.return_value = collection
    mongo_database.database = database

    return ConversationRepository(mongo_database), database


def test_list_recent_returns_messages_in_chronological_order() -> None:
    stored_messages = [
        ConversationMessage(
            conversation_id=TEST_CONVERSATION_ID,
            role=ConversationRole.ASSISTANT,
            content=TEST_CHAT_ANSWER,
            created_at=TEST_MESSAGE_CREATED_AT,
        ),
        ConversationMessage(
            conversation_id=TEST_CONVERSATION_ID,
            role=ConversationRole.USER,
            content=TEST_CHAT_MESSAGE,
            created_at=TEST_MESSAGE_CREATED_AT,
        ),
    ]
    stored_documents = []

    for message in stored_messages:
        document = message.model_dump()
        document[MONGODB_CONVERSATION_ID_FIELD] = str(message.conversation_id)
        stored_documents.append(document)

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter(stored_documents)
    collection = MagicMock()
    collection.find.return_value = cursor
    repository, database = _create_repository(collection)

    messages = asyncio.run(
        repository.list_recent(
            TEST_CONVERSATION_ID,
            TEST_CONVERSATION_CONTEXT_MESSAGES,
        )
    )

    database.__getitem__.assert_called_once_with(CONVERSATION_COLLECTION_NAME)
    collection.find.assert_called_once_with(
        {MONGODB_CONVERSATION_ID_FIELD: str(TEST_CONVERSATION_ID)},
        projection={MONGODB_ID_FIELD: False},
    )
    cursor.sort.assert_called_once_with(MONGODB_ID_FIELD, DESCENDING)
    cursor.limit.assert_called_once_with(TEST_CONVERSATION_CONTEXT_MESSAGES)
    assert [message.role for message in messages] == [
        ConversationRole.USER,
        ConversationRole.ASSISTANT,
    ]


def test_append_turn_stores_user_and_assistant_messages() -> None:
    collection = MagicMock()
    collection.insert_many = AsyncMock()
    repository, database = _create_repository(collection)

    asyncio.run(
        repository.append_turn(
            TEST_CONVERSATION_ID,
            TEST_CHAT_MESSAGE,
            TEST_CHAT_ANSWER,
        )
    )

    database.__getitem__.assert_called_once_with(CONVERSATION_COLLECTION_NAME)
    collection.insert_many.assert_awaited_once()
    documents = collection.insert_many.await_args.args[0]
    assert len(documents) == EXPECTED_CONVERSATION_MESSAGE_COUNT
    stored_messages = [
        ConversationMessage.model_validate(document) for document in documents
    ]
    assert [message.role for message in stored_messages] == [
        ConversationRole.USER,
        ConversationRole.ASSISTANT,
    ]
    assert all(
        document[MONGODB_CONVERSATION_ID_FIELD] == str(TEST_CONVERSATION_ID)
        for document in documents
    )
