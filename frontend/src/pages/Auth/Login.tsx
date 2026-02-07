/**
 * Login Page
 */
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth.ts'

export default function Login() {
  const { login, loading, error } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [success, setSuccess] = useState(false)

  const handleQuickLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setSuccess(false)
    try {
      await login('demo@cosmicwatch.io', 'Demo@12345')
      setSuccess(true)
    } catch (err) {
      // Error is displayed below
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSuccess(false)

    if (!email || !password) {
      return
    }

    try {
      await login(email, password)
      setSuccess(true)
      setEmail('')
      setPassword('')
    } catch (err) {
      // Error is displayed below
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full glass-card p-8 rounded-xl">
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🛸</div>
          <h1 className="text-3xl font-bold text-cyan-400 font-heading">Cosmic Watch</h1>
          <p className="text-gray-400 text-sm mt-2">Monitor Near-Earth Objects</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm text-cyan-300 mb-2">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              disabled={success}
              className="w-full bg-white/10 border border-cyan-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-400 transition-colors disabled:opacity-50"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm text-cyan-300 mb-2">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={success}
              className="w-full bg-white/10 border border-cyan-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-400 transition-colors disabled:opacity-50"
            />
          </div>

          {error && <div className="text-red-400 text-sm">{error}</div>}
          {success && <div className="text-green-400 text-sm">✓ Login successful! Redirecting to dashboard...</div>}

          <button
            type="submit"
            disabled={loading || success}
            className="w-full bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-all neon-glow"
          >
            {loading ? 'Logging in...' : success ? 'Logged In!' : 'Login'}
          </button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-slate-900 text-gray-400">or</span>
          </div>
        </div>

        <button
          onClick={handleQuickLogin}
          disabled={loading || success}
          className="w-full bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-all"
        >
          {loading ? 'Logging in...' : '🚀 Quick Start (Demo)'}
        </button>

        <p className="text-center text-gray-500 text-xs mt-4">Click "Quick Start" to view the dashboard with sample data</p>
      </div>
    </div>
  )
}
