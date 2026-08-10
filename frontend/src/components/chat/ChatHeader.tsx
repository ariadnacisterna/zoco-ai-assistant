import zocoLogo from '../../assets/brand/zoco-logo.svg'
import { APP_COPY } from '../../constants/app'
import { CHAT_COPY } from '../../constants/chat'

interface ChatHeaderProps {
  isLoading: boolean
  onNewConversation: () => void
  onBackToWelcome: () => void
}

export function ChatHeader({
  isLoading,
  onNewConversation,
  onBackToWelcome,
}: ChatHeaderProps) {
  return (
    <header className="chat-header">
      <h1 className="sr-only">{CHAT_COPY.CHAT_TITLE}</h1>
      <button
        className="chat-brand"
        type="button"
        aria-label={CHAT_COPY.RETURN_TO_WELCOME}
        disabled={isLoading}
        onClick={onBackToWelcome}
      >
        <img src={zocoLogo} alt={APP_COPY.BRAND_NAME} />
        <span className="chat-brand-copy">
          <span className="chat-brand-title">{CHAT_COPY.CHAT_TITLE}</span>
          <span className="chat-brand-status">
            <span className="status-dot" aria-hidden="true" />
            {CHAT_COPY.CHAT_STATUS}
          </span>
        </span>
      </button>

      <button
        className="secondary-button"
        type="button"
        disabled={isLoading}
        onClick={onNewConversation}
      >
        {CHAT_COPY.NEW_CONVERSATION}
      </button>
    </header>
  )
}
