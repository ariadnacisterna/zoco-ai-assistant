import { useEffect, useRef } from 'react'
import { CHAT_COPY, SCROLL_BEHAVIOR } from '../../constants/chat'
import type { ConversationMessage } from '../../types/chat'
import { ChatMessage } from './ChatMessage'

interface ChatMessagesProps {
  messages: ConversationMessage[]
  isLoading: boolean
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: SCROLL_BEHAVIOR.NEW_MESSAGE,
    })
  }, [messages.length])

  return (
    <section className="messages-panel" aria-live="polite" aria-busy={isLoading}>
      <div className="messages-list" role="log">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <article
            className="message-row message-row-assistant"
            aria-label={CHAT_COPY.ASSISTANT_MESSAGE_LABEL}
          >
            <div className="assistant-avatar">
              {CHAT_COPY.ASSISTANT_AVATAR_LABEL}
            </div>
            <div className="message-content">
              <div className="message-bubble loading-message">
                <p>{CHAT_COPY.WRITING_RESPONSE}</p>
              </div>
            </div>
          </article>
        )}

        <div ref={messagesEndRef} />
      </div>
    </section>
  )
}
