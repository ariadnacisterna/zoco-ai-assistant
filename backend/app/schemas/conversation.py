from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import ConversationRole


class ConversationMessage(BaseModel):
    """One user or assistant message stored for conversation memory."""

    conversation_id: UUID
    role: ConversationRole
    content: str
    created_at: datetime
