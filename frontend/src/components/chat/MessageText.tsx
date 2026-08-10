import { Fragment, type ReactNode } from 'react'

const LINE_SEPARATOR = '\n'
const LIST_ITEM_PREFIX = '- '
const BOLD_DELIMITER = '**'
const ITALIC_DELIMITER = '*'
const EMPHASIS_PATTERN = /(\*\*[^*]+\*\*|\*[^*]+\*)/g

interface MessageTextProps {
  content: string
}

function renderInlineText(content: string, lineKey: string): ReactNode[] {
  return content
    .split(EMPHASIS_PATTERN)
    .filter(Boolean)
    .map((segment, segmentIndex) => {
      const segmentKey = `${lineKey}-${segmentIndex}`

      if (
        segment.startsWith(BOLD_DELIMITER) &&
        segment.endsWith(BOLD_DELIMITER)
      ) {
        return (
          <strong key={segmentKey}>
            {segment.slice(BOLD_DELIMITER.length, -BOLD_DELIMITER.length)}
          </strong>
        )
      }

      if (
        segment.startsWith(ITALIC_DELIMITER) &&
        segment.endsWith(ITALIC_DELIMITER)
      ) {
        return (
          <em key={segmentKey}>
            {segment.slice(ITALIC_DELIMITER.length, -ITALIC_DELIMITER.length)}
          </em>
        )
      }

      return <Fragment key={segmentKey}>{segment}</Fragment>
    })
}

export function MessageText({ content }: MessageTextProps) {
  const blocks: ReactNode[] = []
  let listItems: Array<{ content: string; key: string }> = []

  const appendList = () => {
    if (listItems.length === 0) {
      return
    }

    blocks.push(
      <ul key={`list-${blocks.length}`}>
        {listItems.map((item) => (
          <li key={item.key}>{renderInlineText(item.content, item.key)}</li>
        ))}
      </ul>,
    )
    listItems = []
  }

  content.split(LINE_SEPARATOR).forEach((line, lineIndex) => {
    const normalizedLine = line.trim()
    const lineKey = `line-${lineIndex}`

    if (normalizedLine.startsWith(LIST_ITEM_PREFIX)) {
      listItems.push({
        content: normalizedLine.slice(LIST_ITEM_PREFIX.length),
        key: lineKey,
      })
      return
    }

    appendList()

    if (normalizedLine.length > 0) {
      blocks.push(
        <p key={lineKey}>{renderInlineText(normalizedLine, lineKey)}</p>,
      )
    }
  })

  appendList()

  return <div className="formatted-message">{blocks}</div>
}
