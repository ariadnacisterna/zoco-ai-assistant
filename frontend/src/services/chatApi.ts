import { CHAT_CONFIG, HTTP_CONFIG } from '../config/chat'
import { CHAT_COPY } from '../constants/chat'
import {
  CHAT_STATUS,
  type ChatRequest,
  type ChatResponse,
  type ChatSource,
  type ChatStatus,
} from '../types/chat'

interface ErrorResponse {
  detail?: unknown
}

export class ChatApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = new.target.name
    this.status = status
  }
}

function isChatStatus(value: unknown): value is ChatStatus {
  return value === CHAT_STATUS.ANSWERED || value === CHAT_STATUS.HUMAN_FALLBACK
}

function isChatSource(value: unknown): value is ChatSource {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const source = value as Record<string, unknown>

  return (
    typeof source.source_url === 'string' &&
    typeof source.title === 'string' &&
    typeof source.similarity === 'number' &&
    Number.isFinite(source.similarity)
  )
}

function isChatResponse(value: unknown): value is ChatResponse {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const response = value as Record<string, unknown>

  return (
    typeof response.conversation_id === 'string' &&
    isChatStatus(response.status) &&
    typeof response.answer === 'string' &&
    Array.isArray(response.sources) &&
    response.sources.every(isChatSource)
  )
}

function getErrorMessage(value: unknown): string {
  if (typeof value !== 'object' || value === null) {
    return CHAT_COPY.ERROR_DEFAULT
  }

  const response = value as ErrorResponse

  return typeof response.detail === 'string'
    ? response.detail
    : CHAT_COPY.ERROR_DEFAULT
}

function getChatUrl(): string {
  const baseUrl = CHAT_CONFIG.API_BASE_URL.replace(/\/$/, '')
  return `${baseUrl}${CHAT_CONFIG.API_PATH}`
}

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch(getChatUrl(), {
    method: HTTP_CONFIG.METHOD_POST,
    headers: {
      [HTTP_CONFIG.CONTENT_TYPE_HEADER]: HTTP_CONFIG.JSON_CONTENT_TYPE,
    },
    body: JSON.stringify(request),
  })

  let responseBody: unknown

  try {
    responseBody = await response.json()
  } catch {
    throw new ChatApiError(CHAT_COPY.ERROR_INVALID_RESPONSE, response.status)
  }

  if (!response.ok) {
    throw new ChatApiError(getErrorMessage(responseBody), response.status)
  }

  if (!isChatResponse(responseBody)) {
    throw new ChatApiError(CHAT_COPY.ERROR_INVALID_RESPONSE, response.status)
  }

  return responseBody
}
