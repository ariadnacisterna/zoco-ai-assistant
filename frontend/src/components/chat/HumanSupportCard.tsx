import { CHAT_CONFIG } from '../../config/chat'
import { EXTERNAL_LINK_PROPS } from '../../constants/app'
import { CHAT_COPY } from '../../constants/chat'

export function HumanSupportCard() {
  return (
    <aside className="human-support-card">
      <div>
        <h3>{CHAT_COPY.HUMAN_SUPPORT_TITLE}</h3>
        <p>{CHAT_COPY.HUMAN_SUPPORT_DESCRIPTION}</p>
      </div>
      <a href={CHAT_CONFIG.HUMAN_SUPPORT_URL} {...EXTERNAL_LINK_PROPS}>
        {CHAT_COPY.HUMAN_SUPPORT_ACTION}
      </a>
    </aside>
  )
}
