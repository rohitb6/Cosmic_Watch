/**
 * Risk Calculator - Client-side CRI calculations
 * Mirrors backend algorithm for consistency
 */

export interface CRIComponents {
  diameter_score: number
  velocity_score: number
  distance_score: number
  hazard_bonus: number
  final_cri: number
}

function sigmoid(x: number): number {
  try {
    return 1 / (1 + Math.exp(-x))
  } catch {
    return x > 0 ? 1 : 0
  }
}

export function calculateCRI(
  diameterKm: number | null,
  velocityKmh: number | null,
  missDistanceKm: number | null,
  isHazardous: boolean
): [number, CRIComponents] {
  const diameter = diameterKm || 0.05
  const velocity = velocityKmh || 15000
  const missDistance = missDistanceKm || 1000000

  // Diameter score
  const diameterNorm = (diameter / 1) * 100
  const diameterScoreRaw = sigmoid(diameterNorm / 10)
  const diameterScore = diameterScoreRaw * 100

  // Velocity score
  const velocityNorm = (velocity / 30000) * 100
  const velocityScoreRaw = sigmoid(velocityNorm / 10)
  const velocityScore = velocityScoreRaw * 100

  // Distance score
  const distanceFactor = 1 / (Math.log(missDistance + 1) + 1)
  const distanceScoreRaw = sigmoid(distanceFactor * 100)
  const distanceScore = distanceScoreRaw * 100

  // Hazard bonus
  const hazardBonus = isHazardous ? 15 : 0

  // Final CRI
  let finalCRI =
    diameterScore * 0.35 +
    velocityScore * 0.25 +
    distanceScore * 0.25 +
    hazardBonus * 0.15

  finalCRI = Math.max(0, Math.min(100, finalCRI))

  return [
    finalCRI,
    {
      diameter_score: Math.round(diameterScore * 100) / 100,
      velocity_score: Math.round(velocityScore * 100) / 100,
      distance_score: Math.round(distanceScore * 100) / 100,
      hazard_bonus: Math.round(hazardBonus * 100) / 100,
      final_cri: Math.round(finalCRI * 100) / 100,
    },
  ]
}

export function getRiskLevel(cri: number) {
  if (cri >= 81) {
    return {
      level: 'CRITICAL',
      emoji: '⛔',
      color: '#FF1744',
      description: 'Rare celestial event - Extremely close approach',
      recommendation: 'High scientific interest - Monitor in real-time',
    }
  } else if (cri >= 61) {
    return {
      level: 'RED',
      emoji: '⚠️',
      color: '#FF6B35',
      description: 'Very close approach - Significant risk',
      recommendation: 'Add to watchlist for continuous monitoring',
    }
  } else if (cri >= 41) {
    return {
      level: 'ORANGE',
      emoji: '🟠',
      color: '#FFA500',
      description: 'High interest - Moderately close approach',
      recommendation: 'Worth tracking for research',
    }
  } else if (cri >= 21) {
    return {
      level: 'YELLOW',
      emoji: '🟡',
      color: '#FFD700',
      description: 'Monitor closely - Notable asteroid',
      recommendation: 'Interesting for astronomy enthusiasts',
    }
  } else {
    return {
      level: 'GREEN',
      emoji: '🟢',
      color: '#00D084',
      description: 'Safe to observe - Low risk approach',
      recommendation: 'Routine asteroid - Safe observation',
    }
  }
}

export function daysUntilApproach(approachDateStr: string): number {
  const approach = new Date(approachDateStr)
  const now = new Date()
  const diff = approach.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return Math.max(0, days)
}

export function isNext72hThreat(approachDateStr: string, cri: number): boolean {
  const days = daysUntilApproach(approachDateStr)
  return days <= 3 && cri >= 40
}
