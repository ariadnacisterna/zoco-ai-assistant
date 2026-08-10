import {
  type KeyboardEvent,
  useEffect,
  useRef,
} from 'react'
import { APP_COPY, DOM_ID, DOM_SELECTOR } from '../../constants/app'
import { CHAT_COPY, KEYBOARD_KEY } from '../../constants/chat'

interface ErrorPopupProps {
  message: string
  onClose: () => void
}

export function ErrorPopup({ message, onClose }: ErrorPopupProps) {
  const popupRef = useRef<HTMLElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const previouslyFocusedElement = document.activeElement

    closeButtonRef.current?.focus()

    return () => {
      if (
        previouslyFocusedElement instanceof HTMLElement &&
        previouslyFocusedElement.isConnected
      ) {
        previouslyFocusedElement.focus()
      }
    }
  }, [])

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key !== KEYBOARD_KEY.TAB) {
      return
    }

    const focusableElements = popupRef.current?.querySelectorAll<HTMLElement>(
      DOM_SELECTOR.FOCUSABLE_ELEMENT,
    )

    if (!focusableElements || focusableElements.length === 0) {
      return
    }

    const firstFocusableElement = focusableElements.item(0)
    const lastFocusableElement = focusableElements.item(
      focusableElements.length - 1,
    )
    const shouldFocusLast =
      event.shiftKey && document.activeElement === firstFocusableElement
    const shouldFocusFirst =
      !event.shiftKey && document.activeElement === lastFocusableElement

    if (!shouldFocusFirst && !shouldFocusLast) {
      return
    }

    event.preventDefault()
    const nextFocusableElement = shouldFocusLast
      ? lastFocusableElement
      : firstFocusableElement
    nextFocusableElement.focus()
  }

  return (
    <div className="popup-backdrop">
      <section
        ref={popupRef}
        className="error-popup"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={DOM_ID.ERROR_TITLE}
        aria-describedby={DOM_ID.ERROR_MESSAGE}
        onKeyDown={handleKeyDown}
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
