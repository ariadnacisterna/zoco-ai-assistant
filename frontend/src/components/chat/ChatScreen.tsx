import type { ConversationMessage } from '../../types/chat'
import { ChatComposer } from './ChatComposer'
import { ChatHeader } from './ChatHeader'
import { ChatMessages } from './ChatMessages'

interface ChatScreenProps {
  messages: ConversationMessage[]
  isLoading: boolean
  onSend: (message: string) => void
  onNewConversation: () => void
  onBackToWelcome: () => void
}

export function ChatScreen({
  messages,
  isLoading,
  onSend,
  onNewConversation,
  onBackToWelcome,
}: ChatScreenProps) {
  return (
    <main className="chat-screen">
      <ChatHeader
        isLoading={isLoading}
        onNewConversation={onNewConversation}
        onBackToWelcome={onBackToWelcome}
      />
      <ChatMessages messages={messages} isLoading={isLoading} />
      <ChatComposer isLoading={isLoading} onSend={onSend} />
    </main>
  )
}
