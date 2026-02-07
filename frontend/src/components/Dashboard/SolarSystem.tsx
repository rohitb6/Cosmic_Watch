/**
 * Live NASA Space Feed Viewer
 * 
 * Copyright © 2026 Rohit. Made with love by Rohit.
 * All rights reserved.
 * 
 * Real-time live video from NASA ISS cameras and space feeds
 */
import React, { useState } from 'react'

type FeedSource = 'iss' | 'nasatv' | 'spacex'

export default function SolarSystem() {
  const [selectedFeed, setSelectedFeed] = useState<FeedSource>('iss')

  const feeds: Record<FeedSource, { name: string; url: string; description: string }> = {
    iss: {
      name: '🛰️ ISS Earth Viewing',
      url: 'https://www.youtube.com/embed/86YLFOog4GM?autoplay=1',
      description: 'Live video feed from International Space Station cameras showing Earth'
    },
    nasatv: {
      name: '📡 NASA TV Live',
      url: 'https://www.youtube.com/embed/21X5lGlDOfg?autoplay=1',
      description: 'NASA Television channel with live space missions and events'
    },
    spacex: {
      name: '🚀 SpaceX Starlink',
      url: 'https://www.youtube.com/embed/j82tavqnIMQ?autoplay=1',
      description: 'SpaceX live launches and space operations feed'
    }
  }

  const currentFeed = feeds[selectedFeed]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-2xl">🌍</div>
          <div>
            <h2 className="text-xl font-bold text-cyan-400 font-heading">Live Space Feed</h2>
            <p className="text-xs text-gray-400">{currentFeed.description}</p>
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
          src={currentFeed.url}
          title={currentFeed.name}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="w-full h-full"
        />
      </div>

      {/* Feed Selection Buttons */}
      <div className="grid grid-cols-3 gap-3">
        {(Object.entries(feeds) as [FeedSource, typeof feeds[FeedSource]][]).map(([key, feed]) => (
          <button
            key={key}
            onClick={() => setSelectedFeed(key)}
            className={`px-4 py-3 rounded-lg font-semibold transition-all text-sm ${
              selectedFeed === key
                ? 'bg-cyan-500/40 text-cyan-300 border border-cyan-400'
                : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10 hover:text-cyan-300'
            }`}
          >
            {feed.name}
          </button>
        ))}
      </div>

      {/* Info */}
      <div className="glass-card p-4 rounded-lg bg-cyan-900/20 border border-cyan-500/30 text-xs text-cyan-300">
        <p className="flex items-start gap-2">
          <span>ℹ️</span>
          <span>
            Watching real-time feeds from NASA and space agencies. ISS orbits Earth every 90 minutes. Video may be unavailable during maintenance or mission changes.
          </span>
        </p>
      </div>
    </div>
  )
}
