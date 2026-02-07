/**
 * Alerts Page
 */
import { useEffect, useState } from 'react'
import apiClient from '@/utils/api.ts'
import { formatDate } from '@/utils/formatters.ts'

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [unreadOnly, setUnreadOnly] = useState(false)

  useEffect(() => {
    fetchAlerts()
  }, [unreadOnly])

  const fetchAlerts = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/alerts', {
        params: { unread_only: unreadOnly, limit: 100 },
      })
      setAlerts(response.data.items)
    } catch (err) {
      console.error('Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleMarkRead = async (alertId: string) => {
    try {
      await apiClient.patch(`/alerts/${alertId}/read`)
      setAlerts(alerts.map((a) => (a.id === alertId ? { ...a, is_read: true } : a)))
    } catch (err) {
      console.error('Failed to mark alert as read')
    }
  }

  const handleDelete = async (alertId: string) => {
    try {
      await apiClient.delete(`/alerts/${alertId}`)
      setAlerts(alerts.filter((a) => a.id !== alertId))
    } catch (err) {
      console.error('Failed to delete alert')
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-cyan-400 font-heading">Alerts</h1>
          <p className="text-gray-400">Threat notifications and watchlist updates</p>
        </div>
        <button
          onClick={() => setUnreadOnly(!unreadOnly)}
          className={`px-4 py-2 rounded-lg border transition-colors ${
            unreadOnly
              ? 'bg-cyan-500/30 border-cyan-400 text-cyan-300'
              : 'bg-transparent border-gray-600 text-gray-400'
          }`}
        >
          Unread Only
        </button>
      </div>

      {loading ? (
        <div className="text-center text-gray-400">Loading alerts...</div>
      ) : alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <AlertItem key={alert.id} alert={alert} onMarkRead={handleMarkRead} onDelete={handleDelete} />
          ))}
        </div>
      ) : (
        <div className="glass-card p-12 rounded-xl text-center text-gray-400">
          <p>No alerts yet</p>
        </div>
      )}
    </div>
  )
}

function AlertItem({
  alert,
  onMarkRead,
  onDelete,
}: {
  alert: any
  onMarkRead: (id: string) => void
  onDelete: (id: string) => void
}) {
  const alertTypeColor =
    alert.alert_type === 'DISTANCE'
      ? 'border-l-cyan-400'
      : alert.alert_type === 'RISK_SCORE'
        ? 'border-l-orange-400'
        : 'border-l-red-400'

  return (
    <div className={`glass-card p-4 rounded-lg border-l-4 ${alertTypeColor} ${!alert.is_read ? 'bg-white/15' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-cyan-300">{alert.asteroid_name}</h4>
            {!alert.is_read && <span className="w-2 h-2 bg-cyan-400 rounded-full pulse-glow"></span>}
          </div>
          <p className="text-xs text-gray-400 mb-2">
            {alert.alert_type.replace(/_/g, ' ')} • {formatDate(alert.triggered_at)}
          </p>
          <p className="text-sm text-gray-300">{alert.triggered_reason}</p>
          {alert.cri_score_at_trigger !== undefined && (
            <p className="text-xs text-cyan-400 mt-1">Risk Score: {alert.cri_score_at_trigger.toFixed(1)}</p>
          )}
        </div>
        <div className="flex gap-2">
          {!alert.is_read && (
            <button
              onClick={() => onMarkRead(alert.id)}
              className="px-3 py-1 rounded-lg bg-cyan-500/30 hover:bg-cyan-500/50 text-cyan-300 text-xs"
            >
              Mark Read
            </button>
          )}
          <button
            onClick={() => onDelete(alert.id)}
            className="px-3 py-1 rounded-lg bg-red-900/30 hover:bg-red-900/50 text-red-300 text-xs"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
