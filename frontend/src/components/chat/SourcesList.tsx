import { EXTERNAL_LINK_PROPS } from '../../constants/app'
import { CHAT_COPY } from '../../constants/chat'
import type { ChatSource } from '../../types/chat'
import { formatSourceLocation } from '../../utils/sourceUrl'

interface SourcesListProps {
  sources: ChatSource[]
}

export function SourcesList({ sources }: SourcesListProps) {
  if (sources.length === 0) {
    return null
  }

  return (
    <section className="sources-list" aria-label={CHAT_COPY.SOURCES_TITLE}>
      <p>{CHAT_COPY.SOURCES_TITLE}</p>
      <ul>
        {sources.map((source) => {
          const sourceLocation = formatSourceLocation(source.source_url)

          return (
            <li key={source.source_url}>
              <a
                href={source.source_url}
                title={source.source_url}
                aria-label={`${CHAT_COPY.OPEN_SOURCE_LABEL}: ${source.title}, ${sourceLocation}`}
                {...EXTERNAL_LINK_PROPS}
              >
                <span className="source-title">{source.title}</span>
                <span className="source-location">{sourceLocation}</span>
              </a>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
