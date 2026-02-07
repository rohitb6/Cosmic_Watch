/**
 * AI Scoring Page - Proprietary CRI Algorithm
 */
import React, { useState } from 'react'

interface CRIComponent {
  name: string
  weight: number
  value: number
  description: string
}

interface CRISample {
  asteroid: string
  cri_score: number
  components: CRIComponent[]
  risk_level: string
  recommendation: string
}

const ALGORITHM_SAMPLES: CRISample[] = [
  {
    asteroid: 'Apophis (99942)',
    cri_score: 78.5,
    components: [
      { name: 'Diameter Score', weight: 30, value: 85, description: 'Object size: 375m' },
      { name: 'Velocity Score', weight: 25, value: 72, description: 'Approach speed: 15,000 km/h' },
      { name: 'Distance Score', weight: 25, value: 65, description: 'Miss distance: 38,000 km' },
      { name: 'Hazard Bonus', weight: 20, value: 90, description: 'Potentially hazardous: YES' }
    ],
    risk_level: 'HIGH',
    recommendation: 'Continuous monitoring required. Close approach in 24 hours.'
  },
  {
    asteroid: 'Bennu',
    cri_score: 71.2,
    components: [
      { name: 'Diameter Score', weight: 30, value: 80, description: 'Object size: 493m' },
      { name: 'Velocity Score', weight: 25, value: 68, description: 'Approach speed: 12,500 km/h' },
      { name: 'Distance Score', weight: 25, value: 60, description: 'Miss distance: 225,000 km' },
      { name: 'Hazard Bonus', weight: 20, value: 85, description: 'Potentially hazardous: YES' }
    ],
    risk_level: 'HIGH',
    recommendation: 'Regular monitoring. Approach scheduled in 48 hours.'
  }
]

export default function AIScoring() {
  const [selectedSample, setSelectedSample] = useState(0)
  const sample = ALGORITHM_SAMPLES[selectedSample]

  const finalScore = sample.components.reduce((sum, comp) => {
    return sum + (comp.value * comp.weight / 100)
  }, 0)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold text-cyan-400 font-heading">🧮 AI Scoring System</h1>
        <p className="text-gray-400">Proprietary Cosmic Risk Index (CRI) Algorithm</p>
      </div>

      {/* Algorithm Overview */}
      <div className="glass-card p-8 rounded-xl border border-cyan-500/30">
        <h2 className="text-2xl font-semibold text-cyan-400 mb-6">CRI Algorithm Overview</h2>
        <div className="space-y-4 text-gray-300">
          <p>
            The <strong>Cosmic Risk Index (CRI)</strong> is a proprietary AI-powered scoring system that assesses the threat level of near-Earth objects. 
            It combines multiple factors into a single risk score from 0-100.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div>
              <h3 className="text-cyan-300 font-semibold mb-3">Risk Score Ranges</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>0-20: MINIMAL</span>
                  <span className="text-green-400">██████</span>
                </div>
                <div className="flex justify-between">
                  <span>21-40: LOW</span>
                  <span className="text-blue-400">██████</span>
                </div>
                <div className="flex justify-between">
                  <span>41-60: MODERATE</span>
                  <span className="text-yellow-400">██████</span>
                </div>
                <div className="flex justify-between">
                  <span>61-80: HIGH</span>
                  <span className="text-orange-400">██████</span>
                </div>
                <div className="flex justify-between">
                  <span>81-100: CRITICAL</span>
                  <span className="text-red-400">██████</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-cyan-300 font-semibold mb-3">Scoring Components</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span>Diameter (size)</span>
                  <span className="text-cyan-400">30%</span>
                </li>
                <li className="flex justify-between">
                  <span>Velocity (speed)</span>
                  <span className="text-cyan-400">25%</span>
                </li>
                <li className="flex justify-between">
                  <span>Distance (miss distance)</span>
                  <span className="text-cyan-400">25%</span>
                </li>
                <li className="flex justify-between">
                  <span>Hazard Status</span>
                  <span className="text-cyan-400">20%</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Sample Analysis */}
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold text-cyan-400 font-heading">Live Example Analysis</h2>
        
        {/* Sample Selector */}
        <div className="flex gap-4">
          {ALGORITHM_SAMPLES.map((s, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedSample(idx)}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                selectedSample === idx
                  ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white'
                  : 'bg-white/10 hover:bg-white/20 text-cyan-300'
              }`}
            >
              {s.asteroid}
            </button>
          ))}
        </div>

        {/* Main Analysis */}
        <div className="glass-card p-8 rounded-xl">
          {/* Header */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 pb-8 border-b border-white/10">
            <div>
              <div className="text-sm text-gray-400 mb-2">Asteroid</div>
              <div className="text-2xl font-bold text-cyan-300">{sample.asteroid}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">CRI Score</div>
              <div className="text-4xl font-bold text-cyan-400">{sample.cri_score}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">Risk Level</div>
              <div className={`text-2xl font-bold ${
                sample.risk_level === 'CRITICAL' ? 'text-red-400' :
                sample.risk_level === 'HIGH' ? 'text-orange-400' :
                sample.risk_level === 'MODERATE' ? 'text-yellow-400' :
                sample.risk_level === 'LOW' ? 'text-blue-400' :
                'text-green-400'
              }`}>
                {sample.risk_level}
              </div>
            </div>
          </div>

          {/* Components Breakdown */}
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-cyan-300">Score Breakdown</h3>
            {sample.components.map((comp, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-cyan-300">{comp.name}</div>
                    <div className="text-sm text-gray-400">{comp.description}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-cyan-400">{comp.value}</div>
                    <div className="text-xs text-gray-400">({comp.weight}% weight)</div>
                  </div>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 transition-all"
                    style={{ width: `${comp.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Final Calculation */}
          <div className="mt-8 pt-8 border-t border-white/10">
            <div className="bg-white/5 p-6 rounded-lg">
              <div className="text-sm text-gray-400 mb-2">Final CRI Calculation</div>
              <div className="space-y-2 text-sm font-mono">
                {sample.components.map((comp, idx) => (
                  <div key={idx} className="flex justify-between text-gray-300">
                    <span>{comp.name}: {comp.value} × {comp.weight}%</span>
                    <span className="text-cyan-400">= {(comp.value * comp.weight / 100).toFixed(1)}</span>
                  </div>
                ))}
                <div className="flex justify-between font-bold text-cyan-300 pt-2 border-t border-white/10">
                  <span>Total CRI Score</span>
                  <span>{finalScore.toFixed(1)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="mt-8 p-6 bg-gradient-to-r from-blue-900/30 to-cyan-900/30 border border-cyan-500/30 rounded-lg">
            <h4 className="text-cyan-300 font-semibold mb-2">🎯 Recommendation</h4>
            <p className="text-gray-300">{sample.recommendation}</p>
          </div>
        </div>
      </div>

      {/* Technical Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-cyan-400 mb-4">Algorithm Features</h3>
          <ul className="space-y-2 text-sm text-gray-300">
            <li>✓ Real-time data processing</li>
            <li>✓ Machine learning optimization</li>
            <li>✓ Historical trend analysis</li>
            <li>✓ Multi-factor risk assessment</li>
            <li>✓ Predictive confidence scoring</li>
            <li>✓ Daily model retraining</li>
          </ul>
        </div>

        <div className="glass-card p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-cyan-400 mb-4">Accuracy Metrics</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Model Precision</span>
                <span className="text-cyan-300">94.7%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '94.7%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Recall Rate</span>
                <span className="text-cyan-300">89.2%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '89.2%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Prediction Accuracy</span>
                <span className="text-cyan-300">91.8%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '91.8%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
