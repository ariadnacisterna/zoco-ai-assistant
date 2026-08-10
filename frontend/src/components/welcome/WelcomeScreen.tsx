import zocoLogo from '../../assets/brand/zoco-logo.svg'
import { APP_COPY, DOM_ID } from '../../constants/app'
import { CHAT_COPY } from '../../constants/chat'

interface WelcomeScreenProps {
  onStart: () => void
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <main className="welcome-screen">
      <section
        className="welcome-panel"
        aria-labelledby={DOM_ID.WELCOME_TITLE}
      >
        <header className="brand-header">
          <img
            className="brand-logo"
            src={zocoLogo}
            alt={APP_COPY.BRAND_NAME}
          />
          <p>{CHAT_COPY.WELCOME_HEADER_LABEL}</p>
        </header>

        <div className="welcome-content">
          <p className="welcome-description">{CHAT_COPY.WELCOME_DESCRIPTION}</p>
          <h1 id={DOM_ID.WELCOME_TITLE}>{CHAT_COPY.WELCOME_TITLE}</h1>
          <button className="primary-button" type="button" onClick={onStart}>
            {CHAT_COPY.START_CONVERSATION}
          </button>
        </div>

        <footer className="welcome-proof">
          <span className="status-dot" aria-hidden="true" />
          {CHAT_COPY.VERIFIED_INFORMATION}
        </footer>
      </section>
    </main>
  )
}
