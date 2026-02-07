import { useState } from 'react'
import apiClient from '../utils/api'

export function useAuth() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const register = async (email: string, username: string, password: string) => {
    setLoading(true)
    try {
      const response = await apiClient.post('/auth/register', {
        email,
        username,
        password,
      })
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      window.dispatchEvent(new Event('auth-change'))
      setError(null)
      return response.data
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed'
      setError(message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    setLoading(true)
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      })
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      window.dispatchEvent(new Event('auth-change'))
      setError(null)
      return response.data
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed'
      setError(message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.dispatchEvent(new Event('auth-change'))
  }

  const getCurrentUser = async () => {
    try {
      const response = await apiClient.get('/auth/me')
      return response.data
    } catch (err: any) {
      throw new Error('Failed to fetch user')
    }
  }

  return {
    loading,
    error,
    register,
    login,
    logout,
    getCurrentUser,
  }
}
