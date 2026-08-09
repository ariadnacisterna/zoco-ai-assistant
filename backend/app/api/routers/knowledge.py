from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError

from app.api.dependencies import get_knowledge_service
from app.core.constants import (
    DATABASE_UNAVAILABLE_MESSAGE,
    KNOWLEDGE_PATH,
    KNOWLEDGE_SOURCE_UNAVAILABLE_MESSAGE,
    KNOWLEDGE_TAG,
)
from app.core.exceptions import KnowledgeSourceUnavailableError
from app.schemas.knowledge import KnowledgeUpdateResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix=KNOWLEDGE_PATH,
    tags=[KNOWLEDGE_TAG],
)


@router.put(
    "",
    response_model=KnowledgeUpdateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_502_BAD_GATEWAY: {
            "description": KNOWLEDGE_SOURCE_UNAVAILABLE_MESSAGE,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": DATABASE_UNAVAILABLE_MESSAGE,
        },
    },
)
async def update_knowledge(
    knowledge_service: Annotated[
        KnowledgeService,
        Depends(get_knowledge_service),
    ],
) -> KnowledgeUpdateResponse:
    """Update knowledge from configured public sources."""

    try:
        return await knowledge_service.update_knowledge()
    except KnowledgeSourceUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=KNOWLEDGE_SOURCE_UNAVAILABLE_MESSAGE,
        ) from error
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNAVAILABLE_MESSAGE,
        ) from error
