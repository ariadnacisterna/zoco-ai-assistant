from typing import Annotated
from uuid import UUID

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    FiniteFloat,
    StringConstraints,
)

from app.core.enums import ChatStatus

NormalizedMessage = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class ChatRequest(BaseModel):
    """Message sent by the user to the assistant."""

    message: NormalizedMessage
    conversation_id: UUID | None = None


class ChatSource(BaseModel):
    """Public source used to support an answer."""

    source_url: AnyHttpUrl
    title: str
    similarity: FiniteFloat = Field(ge=-1.0, le=1.0)


class ChatResponse(BaseModel):
    """Grounded answer or an explicit human fallback."""

    conversation_id: UUID
    status: ChatStatus
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)
