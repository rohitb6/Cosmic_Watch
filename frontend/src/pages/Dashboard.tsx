/**
 * Dashboard Page - Mission Control Panel
 */
import React, { useEffect } from 'react'
import { useAsteroids } from '@/hooks/useAsteroids.ts'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { asteroids, loading, error, getNext72hThreats } = useAsteroids()

  useEffect(() => {
    getNext72hThreats()
  }, [])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold text-cyan-400 font-heading">Mission Control</h1>
        <p className="text-gray-400">Monitor Near-Earth Objects and assess cosmic threats</p>
      </div>

      {/* Alert Banner */}
      <div className="glass-card p-6 rounded-xl border-l-4 border-red-500 bg-red-900/20">
        <div className="flex items-start gap-4">
          <span className="text-3xl">⚠️</span>
          <div>
            <h3 className="font-semibold text-red-300 mb-1">Next 72 Hours Critical Alert</h3>
            <p className="text-sm text-gray-400">
              {asteroids.length} cosmic events require attention. Review threats below.
            </p>
          </div>
        </div>
      </div>

      {/* Threats Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Next 72h Threats */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-2xl font-semibold text-cyan-400 font-heading">Next 72 Hours Threats</h2>

          {loading ? (
            <div className="glass-card p-8 rounded-xl flex items-center justify-center">
              <div className="pulse-glow text-2xl">Loading threats...</div>
            </div>
          ) : error ? (
            <div className="glass-card p-6 rounded-xl border border-red-500/50 bg-red-900/20">
              <p className="text-red-300">{error}</p>
            </div>
          ) : asteroids.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {asteroids.slice(0, 6).map((asteroid) => (
                <ThreatCard key={asteroid.id} asteroid={asteroid} />
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 rounded-xl text-center text-gray-400">
              No significant threats in the next 72 hours.
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="glass-card p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-cyan-400 mb-4">Quick Stats</h3>
          <div className="space-y-3 text-sm">
            <StatRow label="Critical Threats" value={asteroids.filter((a) => (a.cri_score ?? 0) >= 81).length} />
            <StatRow label="Monitored Asteroids" value="--" />
            <StatRow label="Active Alerts" value="--" />
            <StatRow label="Last Sync" value="Just now" />
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="glass-card p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-cyan-400 mb-4">Risk Distribution</h3>
          <RiskDistributionChart asteroids={asteroids} />
        </div>
      </div>

      {/* Info Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <Link to="/observatory">
          <InfoCard title="🔭 Observatory" text="Real-time NASA NeoWs API data" />
        </Link>
        <Link to="/ai-scoring">
          <InfoCard title="🧮 AI Scoring" text="Proprietary CRI algorithm" />
        </Link>
        <Link to="/watchlist">
          <InfoCard title="📊 Watchlist" text="Track and customize alerts" />
        </Link>
      </div>
    </div>
  )
}

function ThreatCard({ asteroid }: { asteroid: any }) {
  const riskColor =
    (asteroid.cri_score ?? 0) >= 81
      ? 'text-red-400'
      : (asteroid.cri_score ?? 0) >= 61
        ? 'text-orange-400'
        : (asteroid.cri_score ?? 0) >= 41
          ? 'text-yellow-400'
          : 'text-green-400'

  return (
    <Link to={`/asteroid/${asteroid.id}`}>
      <div className="glass-card p-4 rounded-lg hover:scale-105 transition-transform cursor-pointer">
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-semibold text-cyan-300 truncate flex-1">{asteroid.name}</h4>
          <span className={`text-lg font-bold ${riskColor}`}>{asteroid.cri_score?.toFixed(1)}</span>
        </div>
        <p className="text-xs text-gray-400 mb-3">{asteroid.neo_id}</p>
        <div className="text-xs space-y-1 text-gray-400">
          <div>⌀ {asteroid.diameter_km?.toFixed(2) || '--'} km</div>
          <div>🚀 {asteroid.is_hazardous ? 'Hazardous ⚠️' : 'Safe'}</div>
        </div>
      </div>
    </Link>
  )
}

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between items-center pb-2 border-b border-white/10">
      <span className="text-gray-400">{label}</span>
      <span className="font-semibold text-cyan-300">{value}</span>
    </div>
  )
}

function InfoCard({ title, text }: { title: string; text: string }) {
  return (
    <div className="glass-card p-4 rounded-lg text-center hover:scale-105 hover:border-cyan-400/50 transition-all cursor-pointer">
      <p className="font-semibold mb-2">{title}</p>
      <p className="text-xs text-gray-400">{text}</p>
    </div>
  )
}

function RiskDistributionChart({ asteroids }: { asteroids: any[] }) {
  const critical = asteroids.filter((a) => (a.cri_score ?? 0) >= 81).length
  const high = asteroids.filter((a) => (a.cri_score ?? 0) >= 61 && (a.cri_score ?? 0) < 81).length
  const medium = asteroids.filter((a) => (a.cri_score ?? 0) >= 41 && (a.cri_score ?? 0) < 61).length
  const low = asteroids.filter((a) => (a.cri_score ?? 0) < 41).length
  const total = critical + high + medium + low

  if (total === 0) return <p className="text-gray-400 text-xs">No data</p>

  return (
    <div className="space-y-2">
      <BarSegment label="Critical" count={critical} total={total} color="bg-red-600" />
      <BarSegment label="High" count={high} total={total} color="bg-orange-600" />
      <BarSegment label="Medium" count={medium} total={total} color="bg-yellow-600" />
      <BarSegment label="Low" count={low} total={total} color="bg-green-600" />
    </div>
  )
}

function BarSegment({
  label,
  count,
  total,
  color,
}: {
  label: string
  count: number
  total: number
  color: string
}) {
  const percentage = (count / total) * 100

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-cyan-300">{count}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  )
}
