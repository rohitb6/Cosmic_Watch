/**
 * Cosmic Watch - Real-time Asteroid Monitoring & AI Chatbot
 * 
 * Copyright © 2026 Rohit. Made with love by Rohit.
 * All rights reserved.
 * 
 * Repository: https://github.com/rohitb6/Cosmic_Watch
 */

import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import ChatBot from './components/Common/ChatBot'
import Dashboard from './pages/Dashboard'
import AsteroidDetail from './pages/AsteroidDetail'
import Watchlist from './pages/Watchlist'
import Alerts from './pages/Alerts'
import Observatory from './pages/Observatory'
import AIScoring from './pages/AIScoring'
import Login from './pages/Auth/Login'
import './styles/globals.css'

function AppRoutes({ isAuthenticated }: { isAuthenticated: boolean }) {
  const location = useLocation()
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  // If authenticated and on auth page, redirect to dashboard
  if (isAuthenticated && isAuthPage) {
    return <Navigate to="/" replace />
  }

  // If not authenticated and trying to access protected route, redirect to login
  if (!isAuthenticated && !isAuthPage) {
    return <Navigate to="/login" replace />
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/asteroid/:id" element={<AsteroidDetail />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/observatory" element={<Observatory />} />
        <Route path="/ai-scoring" element={<AIScoring />} />
      </Route>
    </Routes>
  )
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'))

  useEffect(() => {
    const handleAuthChange = () => {
      // Small delay to ensure localStorage is fully updated
      setTimeout(() => {
        setIsAuthenticated(!!localStorage.getItem('access_token'))
      }, 50)
    }

    window.addEventListener('auth-change', handleAuthChange)
    window.addEventListener('storage', handleAuthChange)
    return () => {
      window.removeEventListener('auth-change', handleAuthChange)
      window.removeEventListener('storage', handleAuthChange)
    }
  }, [])

  return (
    <BrowserRouter>
      <AppRoutes isAuthenticated={isAuthenticated} />
      {isAuthenticated && <ChatBot />}
    </BrowserRouter>
  )
}

export default App
