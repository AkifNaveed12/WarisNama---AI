import { endpoints } from '../../../services/endpoints'

export const sendMessage = async (message, sessionId = null) => {
  const response = await endpoints.chat(message, sessionId)
  return response.data
}