import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.knowledge_scheduler import KnowledgeScheduler
from app.services.knowledge_service import KnowledgeService

TEST_UPDATE_INTERVAL_HOURS = 1
EXPECTED_UPDATE_INTERVAL_SECONDS = 3_600.0


def test_scheduler_waits_before_refreshing_existing_knowledge() -> None:
    knowledge_service = Mock(spec=KnowledgeService)
    knowledge_service.update_knowledge = AsyncMock()
    scheduler = KnowledgeScheduler(
        knowledge_service,
        TEST_UPDATE_INTERVAL_HOURS,
    )
    sleep = AsyncMock(side_effect=asyncio.CancelledError)

    with (
        patch("app.services.knowledge_scheduler.asyncio.sleep", sleep),
        pytest.raises(asyncio.CancelledError),
    ):
        asyncio.run(scheduler._run(update_immediately=False))

    sleep.assert_awaited_once_with(EXPECTED_UPDATE_INTERVAL_SECONDS)
    knowledge_service.update_knowledge.assert_not_awaited()


def test_scheduler_refreshes_empty_knowledge_before_waiting() -> None:
    knowledge_service = Mock(spec=KnowledgeService)
    knowledge_service.update_knowledge = AsyncMock()
    scheduler = KnowledgeScheduler(
        knowledge_service,
        TEST_UPDATE_INTERVAL_HOURS,
    )
    sleep = AsyncMock(side_effect=asyncio.CancelledError)

    with (
        patch("app.services.knowledge_scheduler.asyncio.sleep", sleep),
        pytest.raises(asyncio.CancelledError),
    ):
        asyncio.run(scheduler._run(update_immediately=True))

    knowledge_service.update_knowledge.assert_awaited_once_with()
    sleep.assert_awaited_once_with(EXPECTED_UPDATE_INTERVAL_SECONDS)
