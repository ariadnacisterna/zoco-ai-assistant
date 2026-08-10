import { useEffect, useRef } from 'react'
import { APP_COPY, DOM_ID } from '../../constants/app'
import { CHAT_COPY } from '../../constants/chat'

interface ErrorPopupProps {
  message: string
  onClose: () => void
}

export function ErrorPopup({ message, onClose }: ErrorPopupProps) {
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    closeButtonRef.current?.focus()
  }, [])

  return (
    <div className="popup-backdrop">
      <section
        className="error-popup"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={DOM_ID.ERROR_TITLE}
        aria-describedby={DOM_ID.ERROR_MESSAGE}
      >
        <p className="error-popup-label">{APP_COPY.BRAND_NAME}</p>
        <h2 id={DOM_ID.ERROR_TITLE}>{CHAT_COPY.ERROR_TITLE}</h2>
        <p id={DOM_ID.ERROR_MESSAGE}>{message}</p>
        <button ref={closeButtonRef} type="button" onClick={onClose}>
          {CHAT_COPY.ERROR_CLOSE}
        </button>
      </section>
    </div>
  )
}
