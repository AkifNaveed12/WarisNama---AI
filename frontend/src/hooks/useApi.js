import { useState } from 'react'

export const useApi = (apiCall) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null)

  const execute = async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiCall(...args)
      setData(response.data)
      return response.data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { execute, loading, error, data }
}