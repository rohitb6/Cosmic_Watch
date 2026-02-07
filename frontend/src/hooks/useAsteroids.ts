import { useEffect, useState } from 'react'
import apiClient from '../utils/api'

interface Asteroid {
  id: string
  neo_id: string
  name: string
  diameter_km?: number
  is_hazardous: boolean
  cri_score?: number
  risk_level?: {
    level: string
    emoji: string
    color: string
    description: string
  }
}

export function useAsteroids() {
  const [asteroids, setAsteroids] = useState<Asteroid[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Sync NASA data to database
  const syncNasaData = async (daysAhead = 7) => {
    try {
      const response = await apiClient.post('/neo/sync-nasa', null, {
        params: { days_ahead: daysAhead },
      })
      console.log('NASA sync result:', response.data)
      return response.data
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to sync NASA data'
      console.error('Sync error:', message)
      throw new Error(message)
    }
  }

  const fetchAsteroids = async (page = 1, limit = 20) => {
    setLoading(true)
    try {
      const response = await apiClient.get('/neo/feed', {
        params: { page, limit, sort: 'risk_desc' },
      })
      setAsteroids(response.data.items || response.data)
      setError(null)
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch asteroids'
      setError(message)
      setAsteroids([])
    } finally {
      setLoading(false)
    }
  }

  const getNext72hThreats = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/neo/next-72h')
      
      // Handle different response formats
      const data = response.data
      const threats = Array.isArray(data) ? data : data.threats || data.items || []
      
      setAsteroids(threats)
      setError(null)
      return threats
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch threats'
      setError(message)
      setAsteroids([])
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const searchAsteroids = async (query: string) => {
    setLoading(true)
    try {
      const response = await apiClient.get('/neo/search', {
        params: { q: query, limit: 10 },
      })
      setAsteroids(response.data)
      setError(null)
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Search failed'
      setError(message)
      setAsteroids([])
    } finally {
      setLoading(false)
    }
  }

  return {
    asteroids,
    loading,
    error,
    fetchAsteroids,
    getNext72hThreats,
    searchAsteroids,
    syncNasaData,
  }
}
