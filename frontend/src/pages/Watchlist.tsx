/**
 * Watchlist Page
 */
import { useEffect, useState } from 'react'
import apiClient from '@/utils/api.ts'

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchWatchlist()
  }, [])

  const fetchWatchlist = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/watchlist')
      setWatchlist(response.data.items)
      setError(null)
    } catch (err: any) {
      setError('Failed to load watchlist')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (asteroidId: string) => {
    try {
      await apiClient.delete(`/watchlist/${asteroidId}`)
      setWatchlist(watchlist.filter((item) => item.asteroid.id !== asteroidId))
    } catch (err) {
      setError('Failed to remove from watchlist')
    }
  }

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold text-cyan-400 font-heading">My Watchlist</h1>
        <p className="text-gray-400">Asteroids you're tracking with custom alerts</p>
      </div>

      {loading ? (
        <div className="text-center text-gray-400">Loading...</div>
      ) : error ? (
        <div className="glass-card p-6 rounded-xl border border-red-500/50 bg-red-900/20">
          <p className="text-red-300">{error}</p>
        </div>
      ) : watchlist.length > 0 ? (
        <div className="space-y-4">
          {watchlist.map((item) => (
            <WatchlistCard key={item.id} item={item} onRemove={handleRemove} />
          ))}
        </div>
      ) : (
        <div className="glass-card p-12 rounded-xl text-center text-gray-400">
          <p className="mb-4">Your watchlist is empty</p>
          <p className="text-sm">Start tracking asteroids from the dashboard</p>
        </div>
      )}
    </div>
  )
}

function WatchlistCard({ item, onRemove }: { item: any; onRemove: (id: string) => void }) {
  return (
    <div className="glass-card p-6 rounded-xl flex items-start justify-between">
      <div className="flex-1">
        <h3 className="text-xl font-semibold text-cyan-300 mb-2">{item.asteroid.name}</h3>
        <p className="text-sm text-gray-400 mb-4">{item.asteroid.neo_id}</p>
        {item.custom_notes && <p className="text-sm text-cyan-400 italic">"{item.custom_notes}"</p>}
      </div>
      <button
        onClick={() => onRemove(item.asteroid.id)}
        className="px-4 py-2 rounded-lg bg-red-900/30 hover:bg-red-900/50 text-red-300 text-sm"
      >
        Remove
      </button>
    </div>
  )
}
