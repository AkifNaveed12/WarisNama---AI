import { useState, useCallback } from 'react'
import { sendMessage } from '../services/chatbotService'

export const useChatbot = () => {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)

  const send = useCallback(async (userMessage) => {
    setLoading(true)
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    try {
      const res = await sendMessage(userMessage, sessionId)
      if (res.session_id && !sessionId) setSessionId(res.session_id)
      setMessages(prev => [...prev, { role: 'assistant', content: res.response }])
      return res
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, an error occurred.' }])
      throw err
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  const clear = useCallback(() => {
    setMessages([])
    setSessionId(null)
  }, [])

  return { messages, loading, send, clear }
}