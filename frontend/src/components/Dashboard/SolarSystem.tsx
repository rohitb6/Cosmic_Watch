/**
 * Live Solar System YouTube Stream
 * 
 * Copyright © 2026 Rohit. Made with love by Rohit.
 * All rights reserved.
 * 
 * Real-time live video stream of solar system from YouTube
 */
import React from 'react'

export default function SolarSystem() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-2xl">🌍</div>
          <div>
            <h2 className="text-xl font-bold text-cyan-400 font-heading">Live Solar System</h2>
            <p className="text-xs text-gray-400">Real-time solar system visualization stream</p>
          </div>
        </div>
        <div className="text-xs text-green-400 flex items-center gap-1">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          LIVE
        </div>
      </div>

      {/* Video Container */}
      <div className="w-full aspect-video rounded-lg overflow-hidden border border-cyan-500/30 bg-black">
        <iframe
          width="100%"
          height="100%"
          src="https://www.youtube.com/embed/fO9e9jnhYK8?autoplay=1"
          title="Live Solar System"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="w-full h-full"
        />
      </div>

      {/* Info */}
      <div className="glass-card p-4 rounded-lg bg-cyan-900/20 border border-cyan-500/30 text-xs text-cyan-300">
        <p className="flex items-start gap-2">
          <span>ℹ️</span>
          <span>
            Watching live solar system stream. This real-time visualization shows the current positions and movements of celestial bodies.
          </span>
        </p>
      </div>
    </div>
  )
}
