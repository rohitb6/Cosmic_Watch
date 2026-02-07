/**
 * AI Chatbot Component - Conversational Interface for Asteroid Monitoring
 * Floating chat widget with full conversation history
 */
import React, { useEffect, useState, useRef } from 'react'
import api from '@/utils/api.ts'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: "👋 Welcome to Cosmic Watch AI! I'm your intelligent assistant for asteroid monitoring and planetary defense. Ask me about asteroids, risk assessment, how to use our platform, or anything related to NEO tracking. What can I help you with?",
          timestamp: new Date().toISOString()
        }
      ])
    }
  }, [isOpen])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await api.post('/chat/message', {
        message: inputValue,
        conversation_id: conversationId
      })

      if (response.data.conversation_id !== conversationId) {
        setConversationId(response.data.conversation_id)
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: "Chat cleared! Start a new conversation. Ask me anything about asteroids, risk assessment, or NEO monitoring.",
        timestamp: new Date().toISOString()
      }
    ])
    setConversationId(null)
  }

  return (
    <>
      {/* Chat Button - Floating Widget */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 shadow-lg flex items-center justify-center text-white text-2xl transition-all hover:scale-110"
        title="Open AI Chatbot"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-40 w-96 max-w-[calc(100vw-2rem)] rounded-2xl bg-gradient-to-b from-slate-900 to-slate-800 border border-cyan-500/30 shadow-2xl overflow-hidden flex flex-col h-[600px]">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-600 to-blue-600 p-4 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-lg">Cosmic Watch AI</h3>
              <p className="text-xs text-cyan-100">Asteroid Expert Assistant</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-cyan-200 transition"
            >
              ✕
            </button>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-900/50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-sm px-4 py-2 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-cyan-600 text-white rounded-br-none'
                      : 'bg-slate-700 text-cyan-100 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-700 text-cyan-100 px-4 py-2 rounded-lg rounded-bl-none">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-cyan-500/20 p-4 bg-slate-900/80 space-y-2">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about asteroids, risk, monitoring..."
                className="flex-1 bg-slate-800 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 text-sm"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 font-semibold transition-all text-sm"
              >
                Send
              </button>
            </div>
            
            <button
              onClick={clearChat}
              className="w-full text-xs text-gray-400 hover:text-cyan-300 transition py-1"
            >
              Clear Chat
            </button>
          </div>
        </div>
      )}
    </>
  )
}
