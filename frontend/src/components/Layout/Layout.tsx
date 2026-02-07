/**
 * Main Layout Component with Navigation
 */
import React, { useState } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth.ts'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Sidebar */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-20'} glass-card transition-all duration-300 rounded-none border-r border-cyan-500/20`}
      >
        <div className="p-6 flex items-center justify-between">
          <div className={`${!sidebarOpen && 'hidden'} flex items-center gap-2`}>
            <div className="text-2xl font-bold text-cyan-400">🛸</div>
            <div className="font-heading text-lg text-cyan-400">Cosmic Watch</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-8 px-4 space-y-2">
          <NavLink to="/" icon="📊" label="Dashboard" open={sidebarOpen} />
          <NavLink to="/observatory" icon="🔭" label="Observatory" open={sidebarOpen} />
          <NavLink to="/ai-scoring" icon="🧮" label="AI Scoring" open={sidebarOpen} />
          <NavLink to="/watchlist" icon="⭐" label="Watchlist" open={sidebarOpen} />
          <NavLink to="/alerts" icon="🚨" label="Alerts" open={sidebarOpen} />
        </nav>

        {/* Bottom Actions */}
        <div className="absolute bottom-6 left-4 right-4 space-y-2">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full py-2 px-3 rounded-lg hover:bg-cyan-500/20 text-cyan-400 text-sm"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
          <button
            onClick={handleLogout}
            className="w-full py-2 px-3 rounded-lg bg-red-900/30 hover:bg-red-900/50 text-red-300 text-sm"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function NavLink({
  to,
  icon,
  label,
  open,
}: {
  to: string
  icon: string
  label: string
  open: boolean
}) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-cyan-500/20 transition-colors text-cyan-400 hover:text-cyan-300"
    >
      <span className="text-xl">{icon}</span>
      {open && <span className="text-sm font-medium">{label}</span>}
    </Link>
  )
}
