/**
 * Risk Meter Component - Animated CRI visualization
 */
import React from 'react'
import { getRiskLevel } from '../../utils/riskCalculator'

interface RiskMeterProps {
  score: number
  compact?: boolean
}

export default function RiskMeter({ score, compact = false }: RiskMeterProps) {
  const risk = getRiskLevel(score)
  const percentage = (score / 100) * 100

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
          style={{ backgroundColor: risk.color + '40', borderColor: risk.color, borderWidth: '2px' }}
        >
          {score.toFixed(0)}
        </div>
        <span className="text-xs text-gray-400">{risk.level}</span>
      </div>
    )
  }

  return (
    <div className="glass-card p-6 rounded-xl max-w-xs">
      <h3 className="text-lg font-semibold text-cyan-400 mb-4">Cosmic Risk Index</h3>

      {/* Circular Progress */}
      <div className="flex justify-center mb-6">
        <svg width="120" height="120" className="transform -rotate-90">
          {/* Background circle */}
          <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(0,255,224,0.1)" strokeWidth="8" />

          {/* Progress circle */}
          <circle
            cx="60"
            cy="60"
            r="50"
            fill="none"
            stroke={risk.color}
            strokeWidth="8"
            strokeDasharray={`${(percentage / 100) * 314} 314`}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>

        {/* Score text in center */}
        <div className="absolute flex flex-col items-center justify-center gap-1">
          <div className="text-4xl font-bold" style={{ color: risk.color }}>
            {score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-400">/ 100</div>
        </div>
      </div>

      {/* Risk info */}
      <div className="text-center mb-4">
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="text-2xl">{risk.emoji}</span>
          <span className="font-semibold" style={{ color: risk.color }}>
            {risk.level}
          </span>
        </div>
        <p className="text-xs text-gray-400">{risk.description}</p>
      </div>

      {/* Recommendation */}
      <div className="bg-white/5 rounded-lg p-3 border border-white/10">
        <p className="text-xs text-cyan-300">{risk.recommendation}</p>
      </div>
    </div>
  )
}
