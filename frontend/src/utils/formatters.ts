import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import utc from 'dayjs/plugin/utc'

dayjs.extend(relativeTime)
dayjs.extend(utc)

export function formatDate(date: string | Date): string {
  return dayjs(date).format('MMM DD, YYYY')
}

export function formatDateTime(date: string | Date): string {
  return dayjs(date).format('MMM DD, YYYY HH:mm')
}

export function formatRelativeTime(date: string | Date): string {
  return dayjs(date).fromNow()
}

export function formatDistance(km: number): string {
  if (km < 1000) {
    return `${km.toFixed(0)} km`
  } else if (km < 1000000) {
    return `${(km / 1000).toFixed(1)}K km`
  } else {
    return `${(km / 1000000).toFixed(2)}M km`
  }
}

export function formatVelocity(kmh: number): string {
  return `${kmh.toFixed(2)} km/h`
}

export function formatDiameter(km: number): string {
  if (km < 1) {
    return `${(km * 1000).toFixed(0)} m`
  }
  return `${km.toFixed(2)} km`
}

export function getLunarDistance(km: number): number {
  // 1 lunar distance ≈ 384,400 km
  return km / 384400
}
