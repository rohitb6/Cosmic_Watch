/**
 * Register Page
 */
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth.ts'

export default function Register() {
  const { register, loading, error } = useAuth()
  const [formData, setFormData] = useState({ email: '', username: '', password: '', confirmPassword: '' })
  const [error2, setError2] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError2(null)
    setSuccess(false)

    // Validate password length
    if (formData.password.length < 8) {
      setError2('Password must be at least 8 characters')
      return
    }

    if (formData.password.length > 72) {
      setError2('Password must be 72 characters or less')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError2('Passwords do not match')
      return
    }

    try {
      await register(formData.email, formData.username, formData.password)
      setSuccess(true)
      setFormData({ email: '', username: '', password: '', confirmPassword: '' })
    } catch (err) {
      // Error is displayed
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full glass-card p-8 rounded-xl">
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🛸</div>
          <h1 className="text-3xl font-bold text-cyan-400 font-heading">Cosmic Watch</h1>
          <p className="text-gray-400 text-sm mt-2">Join the mission</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-cyan-300 mb-2">Email</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={success}
              className="w-full bg-white/10 border border-cyan-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-400 transition-colors disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm text-cyan-300 mb-2">Username</label>
            <input
              type="text"
              name="username"
              placeholder="Enter your username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={success}
              className="w-full bg-white/10 border border-cyan-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-400 transition-colors disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm text-cyan-300 mb-2">Password</label>
            <input
              type="password"
              name="password"
              placeholder="Enter password (8-72 characters)"
              value={formData.password}
              onChange={handleChange}
              maxLength={72}
              required
              disabled={success}
              className="w-full bg-white/10 border border-cyan-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-400 transition-colors disabled:opacity-50"
            />
            <div className="text-xs text-gray-500 mt-1">Min 8 characters, max 72 characters</div>
          </div>

          <div>
            <label className="block text-sm text-cyan-300 mb-2">Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              placeholder="Re-enter your password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={success}
              className="w-full bg-white/10 border border-cyan-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-400 transition-colors disabled:opacity-50"
            />
          </div>

          {(error || error2) && <div className="text-red-400 text-sm">{error || error2}</div>}
          {success && <div className="text-green-400 text-sm">✓ Account created! Redirecting to dashboard...</div>}

          <button
            type="submit"
            disabled={loading || success}
            className="w-full bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-all neon-glow"
          >
            {loading ? 'Creating account...' : success ? 'Account Created!' : 'Register'}
          </button>
        </form>

        <p className="text-center text-gray-400 text-sm mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-cyan-400 hover:text-cyan-300">
            Login
          </Link>
        </p>
      </div>
    </div>
  )
}
