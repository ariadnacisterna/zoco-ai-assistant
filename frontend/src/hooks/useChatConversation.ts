import { useState } from 'react'
import { CHAT_CONFIG } from '../config/chat'
import { CHAT_COPY } from '../constants/chat'
import { ChatApiError, sendChatMessage } from '../services/chatApi'
import type { ConversationMessage } from '../types/chat'
import {
  createAssistantMessage,
  createInitialMessage,
  createUserMessage,
} from '../utils/chatMessages'

export function useChatConversation() {
  const [isConversationStarted, setIsConversationStarted] = useState(false)
  const [conversationId, setConversationId] = useState<string>()
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string>()

  const startNewConversation = () => {
    setConversationId(undefined)
    setMessages([createInitialMessage()])
    setErrorMessage(undefined)
    setIsConversationStarted(true)
  }

  const returnToWelcome = () => {
    setConversationId(undefined)
    setMessages([])
    setErrorMessage(undefined)
    setIsConversationStarted(false)
  }

  const closeError = () => {
    setErrorMessage(undefined)
  }

  const sendMessage = async (message: string) => {
    if (message.length > CHAT_CONFIG.MAX_MESSAGE_LENGTH) {
      setErrorMessage(CHAT_COPY.ERROR_MESSAGE_TOO_LONG)
      return
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      createUserMessage(message),
    ])
    setIsLoading(true)
    setErrorMessage(undefined)

    try {
      const response = await sendChatMessage({
        message,
        ...(conversationId ? { conversation_id: conversationId } : {}),
      })

      setConversationId(response.conversation_id)
      setMessages((currentMessages) => [
        ...currentMessages,
        createAssistantMessage(response),
      ])
    } catch (error) {
      const message =
        error instanceof ChatApiError ? error.message : CHAT_COPY.ERROR_DEFAULT
      setErrorMessage(message)
    } finally {
      setIsLoading(false)
    }
  }

  return {
    isConversationStarted,
    messages,
    isLoading,
    errorMessage,
    startNewConversation,
    returnToWelcome,
    closeError,
    sendMessage,
  }
}
