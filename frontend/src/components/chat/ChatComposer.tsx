import { type FormEvent, type KeyboardEvent, useState } from 'react'
import { CHAT_CONFIG } from '../../config/chat'
import { CHAT_COPY, KEYBOARD_KEY } from '../../constants/chat'

interface ChatComposerProps {
  isLoading: boolean
  onSend: (message: string) => void
}

export function ChatComposer({ isLoading, onSend }: ChatComposerProps) {
  const [draft, setDraft] = useState('')
  const normalizedDraft = draft.trim()
  const remainingCharacters = CHAT_CONFIG.MAX_MESSAGE_LENGTH - draft.length
  const isSendDisabled = normalizedDraft.length === 0 || isLoading

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isSendDisabled) {
      return
    }

    onSend(normalizedDraft)
    setDraft('')
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === KEYBOARD_KEY.ENTER && !event.shiftKey) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <footer className="composer-area">
      <form className="message-composer" onSubmit={handleSubmit}>
        <label>
          <span className="sr-only">{CHAT_COPY.MESSAGE_INPUT_LABEL}</span>
          <textarea
            value={draft}
            maxLength={CHAT_CONFIG.MAX_MESSAGE_LENGTH}
            placeholder={CHAT_COPY.MESSAGE_PLACEHOLDER}
            disabled={isLoading}
            rows={CHAT_CONFIG.MESSAGE_INPUT_ROWS}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
          />
        </label>
        <button
          className="send-button"
          type="submit"
          disabled={isSendDisabled}
        >
          {CHAT_COPY.SEND_MESSAGE}
        </button>
      </form>
      <p className="character-counter">
        {remainingCharacters} {CHAT_COPY.CHARACTER_LIMIT_LABEL}
      </p>
    </footer>
  )
}
