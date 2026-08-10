from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError

from app.api.dependencies import get_chat_service
from app.core.constants import (
    CHAT_MESSAGE_TOO_LONG_MESSAGE,
    CHAT_PATH,
    CHAT_TAG,
    DATABASE_UNAVAILABLE_MESSAGE,
)
from app.core.exceptions import ChatMessageTooLongError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(
    prefix=CHAT_PATH,
    tags=[CHAT_TAG],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": CHAT_MESSAGE_TOO_LONG_MESSAGE,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": DATABASE_UNAVAILABLE_MESSAGE,
        },
    },
)
async def answer_chat(
    request: ChatRequest,
    chat_service: Annotated[
        ChatService,
        Depends(get_chat_service),
    ],
) -> ChatResponse:
    """Answer a question using verified ZOCO knowledge."""

    try:
        return await chat_service.answer(
            request.message,
            request.conversation_id,
        )
    except ChatMessageTooLongError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=CHAT_MESSAGE_TOO_LONG_MESSAGE,
        ) from error
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNAVAILABLE_MESSAGE,
        ) from error
