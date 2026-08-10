import asyncio
import logging
from contextlib import suppress
from datetime import timedelta

from app.core.constants import (
    AUTOMATIC_KNOWLEDGE_UPDATE_ERROR_MESSAGE,
)
from app.services.knowledge_service import KnowledgeService

LOGGER = logging.getLogger(__name__)


class KnowledgeScheduler:
    """Run automatic knowledge updates at a configured interval."""

    def __init__(
        self,
        knowledge_service: KnowledgeService,
        interval_hours: int,
    ) -> None:
        self._knowledge_service = knowledge_service
        self._interval_seconds = timedelta(hours=interval_hours).total_seconds()
        self._task: asyncio.Task[None] | None = None

    def start(self, update_immediately: bool = True) -> None:
        """Start the automatic update task."""

        if self._task is None:
            self._task = asyncio.create_task(self._run(update_immediately))

    async def stop(self) -> None:
        """Stop the automatic update task."""

        if self._task is None:
            return

        self._task.cancel()

        with suppress(asyncio.CancelledError):
            await self._task

        self._task = None

    async def _run(self, update_immediately: bool) -> None:
        if not update_immediately:
            await asyncio.sleep(self._interval_seconds)

        while True:
            try:
                await self._knowledge_service.update_knowledge()
            except Exception:
                LOGGER.exception(AUTOMATIC_KNOWLEDGE_UPDATE_ERROR_MESSAGE)

            await asyncio.sleep(self._interval_seconds)
