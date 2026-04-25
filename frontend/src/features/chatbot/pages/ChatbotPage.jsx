// import React from 'react'
// import { useChatbot } from '../hooks/useChatbot'
// import ChatWindow from '../components/ChatWindow'

// const ChatbotPage = () => {
//   const { messages, loading, send } = useChatbot()

//   return (
//     <div className="h-full flex flex-col">
//       <h1 className="text-2xl font-bold mb-4">AI Legal Assistant</h1>
//       <div className="flex-1 min-h-0">
//         <ChatWindow messages={messages} loading={loading} onSendMessage={send} />
//       </div>
//     </div>
//   )
// }

// export default ChatbotPage



import React, { useState, useRef, useEffect } from 'react'
import toast from 'react-hot-toast'
import { useChatbot } from '../hooks/useChatbot'
import ChatWindow from '../components/ChatWindow'
import VoiceButton from '../../../components/common/VoiceButton'

const ChatbotPage = () => {
  const { messages, loading, send, clear } = useChatbot()
  const [voiceLanguage, setVoiceLanguage] = useState('ur-PK') // 'ur-PK' or 'en-US'

  const handleVoiceTranscript = (transcript) => {
    if (transcript && transcript.trim()) {
      // Optionally auto‑send the recognized text
      send(transcript)
    } else {
      toast.error('Could not recognize speech. Please try again.')
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">AI Legal Assistant – WarisNama Chatbot</h1>
        <div className="flex items-center gap-2">
          <label className="text-sm">Voice language:</label>
          <select
            value={voiceLanguage}
            onChange={(e) => setVoiceLanguage(e.target.value)}
            className="border rounded p-1 text-sm"
          >
            <option value="ur-PK">Urdu (Pakistan)</option>
            <option value="en-US">English (US)</option>
          </select>
          <VoiceButton onTranscript={handleVoiceTranscript} language={voiceLanguage} />
          <button onClick={clear} className="bg-gray-200 px-3 py-1 rounded text-sm hover:bg-gray-300">
            Clear Chat
          </button>
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <ChatWindow messages={messages} loading={loading} onSendMessage={send} />
      </div>
    </div>
  )
}

export default ChatbotPage