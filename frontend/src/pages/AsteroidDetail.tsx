/**
 * Asteroid Detail Page
 */
import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import apiClient from '@/utils/api.ts'
import RiskMeter from '@/components/Dashboard/RiskMeter.tsx'

export default function AsteroidDetail() {
  const { id } = useParams<{ id: string }>()
  const [asteroid, setAsteroid] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [inWatchlist, setInWatchlist] = useState(false)

  useEffect(() => {
    if (id) {
      fetchAsteroidDetail()
      checkWatchlist()
    }
  }, [id])

  const fetchAsteroidDetail = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/neo/${id}`)
      setAsteroid(response.data)
    } catch (err) {
      console.error('Failed to load asteroid')
    } finally {
      setLoading(false)
    }
  }

  const checkWatchlist = async () => {
    try {
      const response = await apiClient.get(`/watchlist/${id}/status`)
      setInWatchlist(response.data.in_watchlist)
    } catch (err) {
      console.error('Failed to check watchlist')
    }
  }

  const toggleWatchlist = async () => {
    try {
      if (inWatchlist) {
        await apiClient.delete(`/watchlist/${id}`)
      } else {
        await apiClient.post('/watchlist', {
          asteroid_id: id,
          alert_threshold_cri: 40,
        })
      }
      setInWatchlist(!inWatchlist)
    } catch (err) {
      console.error('Failed to toggle watchlist')
    }
  }

  if (loading) {
    return <div className="text-center text-gray-400">Loading asteroid...</div>
  }

  if (!asteroid) {
    return <div className="text-center text-gray-400">Asteroid not found</div>
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-cyan-400 font-heading">{asteroid.name}</h1>
          <p className="text-gray-400">NASA ID: {asteroid.neo_id}</p>
        </div>
        <button
          onClick={toggleWatchlist}
          className={`px-6 py-2 rounded-lg font-semibold transition-all ${
            inWatchlist
              ? 'bg-yellow-500/30 border border-yellow-400 text-yellow-300 neon-glow-warning'
              : 'bg-cyan-500/30 border border-cyan-400 text-cyan-300 neon-glow'
          }`}
        >
          {inWatchlist ? '⭐ In Watchlist' : '+ Add to Watchlist'}
        </button>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Risk Info */}
        <div className="lg:col-span-1">
          {asteroid.cri_score !== undefined && <RiskMeter score={asteroid.cri_score} />}
        </div>

        {/* Center Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Physical Properties */}
          <div className="glass-card p-6 rounded-xl">
            <h2 className="text-xl font-semibold text-cyan-400 mb-4">Physical Properties</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <PropertyRow label="Diameter" value={`${asteroid.diameter_km?.toFixed(3) || '--'} km`} />
              <PropertyRow label="Hazardous" value={asteroid.is_hazardous ? '⚠️ Yes' : '✓ No'} />
              <PropertyRow label="Absolute Magnitude" value={asteroid.absolute_magnitude?.toFixed(2) || '--'} />
              <PropertyRow label="Sentry Object" value={asteroid.is_sentry_object ? 'Yes' : 'No'} />
            </div>
          </div>

          {/* Next Approach */}
          {asteroid.next_approach && (
            <div className="glass-card p-6 rounded-xl">
              <h2 className="text-xl font-semibold text-cyan-400 mb-4">Next Closest Approach</h2>
              <div className="space-y-3 text-sm">
                <PropertyRow
                  label="Date"
                  value={new Date(asteroid.next_approach.closest_approach_date).toLocaleDateString()}
                />
                <PropertyRow label="Miss Distance" value={`${asteroid.next_approach.miss_distance_km?.toFixed(0) || '--'} km`} />
                <PropertyRow label="Velocity" value={`${asteroid.next_approach.approach_velocity_kmh?.toFixed(0) || '--'} km/h`} />
              </div>
            </div>
          )}

          {/* Risk Breakdown */}
          {asteroid.cri_components && (
            <div className="glass-card p-6 rounded-xl">
              <h2 className="text-xl font-semibold text-cyan-400 mb-4">Risk Score Breakdown</h2>
              <div className="space-y-3">
                <ComponentBar label="Diameter Impact" value={asteroid.cri_components.diameter_score} />
                <ComponentBar label="Velocity Factor" value={asteroid.cri_components.velocity_score} />
                <ComponentBar label="Distance Factor" value={asteroid.cri_components.distance_score} />
                <ComponentBar label="Hazard Bonus" value={asteroid.cri_components.hazard_bonus} />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* All Approaches */}
      {asteroid.all_approaches && asteroid.all_approaches.length > 0 && (
        <div className="glass-card p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-cyan-400 mb-4">All Close Approaches</h2>
          <div className="space-y-2">
            {asteroid.all_approaches.map((approach: any, idx: number) => (
              <ApproachRow key={idx} approach={approach} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function PropertyRow({ label, value }: { label: string; value: string | number | React.ReactNode }) {
  return (
    <div className="flex justify-between items-center pb-2 border-b border-white/10">
      <span className="text-gray-400">{label}</span>
      <span className="font-semibold text-cyan-300">{value}</span>
    </div>
  )
}

function ComponentBar({ label, value }: { label: string; value: number }) {
  const percentage = (value / 100) * 100
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-cyan-300 font-semibold">{value.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  )
}

function ApproachRow({ approach }: { approach: any }) {
  return (
    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
      <div className="text-sm">
        <p className="font-semibold text-cyan-300">
          {new Date(approach.closest_approach_date).toLocaleDateString()}
        </p>
        <p className="text-xs text-gray-400">Miss: {approach.miss_distance_km?.toFixed(0) || '--'} km</p>
      </div>
      <div className="text-right">
        <p className="font-semibold text-cyan-300">{approach.calculated_cri?.toFixed(1) || '--'}</p>
        {approach.is_next_72h_threat && <p className="text-xs text-red-400">🛑 Next 72h threat</p>}
      </div>
    </div>
  )
}
