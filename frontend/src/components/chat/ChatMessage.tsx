import { CHAT_COPY } from '../../constants/chat'
import {
  CHAT_STATUS,
  MESSAGE_ROLE,
  type ConversationMessage,
} from '../../types/chat'
import { HumanSupportCard } from './HumanSupportCard'
import { MessageText } from './MessageText'
import { SourcesList } from './SourcesList'

interface ChatMessageProps {
  message: ConversationMessage
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUserMessage = message.role === MESSAGE_ROLE.USER
  const messageLabel = isUserMessage
    ? CHAT_COPY.USER_MESSAGE_LABEL
    : CHAT_COPY.ASSISTANT_MESSAGE_LABEL

  return (
    <article
      className={`message-row ${isUserMessage ? 'message-row-user' : 'message-row-assistant'}`}
      aria-label={messageLabel}
    >
      {!isUserMessage && (
        <div className="assistant-avatar">
          {CHAT_COPY.ASSISTANT_AVATAR_LABEL}
        </div>
      )}

      <div className="message-content">
        <div className="message-bubble">
          {isUserMessage ? (
            <p>{message.content}</p>
          ) : (
            <MessageText content={message.content} />
          )}
        </div>

        {!isUserMessage && <SourcesList sources={message.sources} />}

        {message.status === CHAT_STATUS.HUMAN_FALLBACK && <HumanSupportCard />}
      </div>
    </article>
  )
}
