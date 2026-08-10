import './App.css'
import { ChatScreen } from './components/chat/ChatScreen'
import { ErrorPopup } from './components/feedback/ErrorPopup'
import { WelcomeScreen } from './components/welcome/WelcomeScreen'
import { useChatConversation } from './hooks/useChatConversation'

function App() {
  const chat = useChatConversation()

  return (
    <>
      {chat.isConversationStarted ? (
        <ChatScreen
          messages={chat.messages}
          isLoading={chat.isLoading}
          onSend={chat.sendMessage}
          onNewConversation={chat.startNewConversation}
          onBackToWelcome={chat.returnToWelcome}
        />
      ) : (
        <WelcomeScreen onStart={chat.startNewConversation} />
      )}

      {chat.errorMessage && (
        <ErrorPopup
          message={chat.errorMessage}
          onClose={chat.closeError}
        />
      )}
    </>
  )
}

export default App
