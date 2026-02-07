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

  const fetchAsteroids = async (page = 1, limit = 20) => {
    setLoading(true)
    try {
      const response = await apiClient.get('/neo/feed', {
        params: { page, limit, sort: 'risk_desc' },
      })
      setAsteroids(response.data.items)
      setError(null)
    } catch (err: any) {
      setError(err.message)
      setAsteroids([])
    } finally {
      setLoading(false)
    }
  }

  const getNext72hThreats = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/neo/next-72h')
      setAsteroids(response.data.threats)
      setError(null)
    } catch (err: any) {
      setError(err.message)
      setAsteroids([])
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
      setError(err.message)
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
  }
}
