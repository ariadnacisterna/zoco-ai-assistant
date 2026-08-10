export const CHAT_STATUS = {
  ANSWERED: 'answered',
  HUMAN_FALLBACK: 'human_fallback',
} as const

export type ChatStatus = (typeof CHAT_STATUS)[keyof typeof CHAT_STATUS]

export const MESSAGE_ROLE = {
  USER: 'user',
  ASSISTANT: 'assistant',
} as const

export type MessageRole = (typeof MESSAGE_ROLE)[keyof typeof MESSAGE_ROLE]

export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface ChatSource {
  source_url: string
  title: string
  similarity: number
}

export interface ChatResponse {
  conversation_id: string
  status: ChatStatus
  answer: string
  sources: ChatSource[]
}

export interface ConversationMessage {
  id: string
  role: MessageRole
  content: string
  sources: ChatSource[]
  status?: ChatStatus
}
