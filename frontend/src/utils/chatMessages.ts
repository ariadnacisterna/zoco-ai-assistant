import { CHAT_COPY } from '../constants/chat'
import { MESSAGE_ROLE, type ChatResponse, type ConversationMessage } from '../types/chat'

function createMessageId(): string {
  return crypto.randomUUID()
}

export function createInitialMessage(): ConversationMessage {
  return {
    id: createMessageId(),
    role: MESSAGE_ROLE.ASSISTANT,
    content: CHAT_COPY.INITIAL_MESSAGE,
    sources: [],
  }
}

export function createUserMessage(content: string): ConversationMessage {
  return {
    id: createMessageId(),
    role: MESSAGE_ROLE.USER,
    content,
    sources: [],
  }
}

export function createAssistantMessage(
  response: ChatResponse,
): ConversationMessage {
  return {
    id: createMessageId(),
    role: MESSAGE_ROLE.ASSISTANT,
    content: response.answer,
    sources: response.sources,
    status: response.status,
  }
}
