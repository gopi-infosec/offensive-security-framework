// components/ChatInterface.tsx - FIXED VERSION
'use client'

import { useState, useRef, useEffect } from 'react'
import Message from './Message'
import LoadingSpinner from './LoadingSpinner'
import { Send } from 'lucide-react'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '0',
      role: 'assistant',
      content: `🛡️ Welcome to **Cybersecurity AI Assistant**

I'm your expert guide for all things cybersecurity. I can help you with:

✅ **Web Vulnerabilities** - XSS, SQL Injection, CSRF, SSRF
✅ **Malware Analysis** - Identify and respond to threats
✅ **OWASP Top 10** - Understand critical security risks
✅ **CVE Research** - Latest vulnerabilities and patches
✅ **Best Practices** - Secure coding and architecture
✅ **Incident Response** - How to handle security breaches

Ask me anything about cybersecurity! Type your question below to get started.`,
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      console.log('📤 Sending request to /api/chat')
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(`API Error: ${response.status} - ${errorData.error || 'Unknown error'}`)
      }

      if (!response.body) {
        throw new Error('No response body received from server')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      let fullText = ''
      let messageIndex = messages.length + 1

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        fullText += decoder.decode(value, { stream: true })
        
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1].content = fullText
          return updated
        })
      }

      console.log('✅ Response complete')
    } catch (error) {
      console.error('❌ Error:', error)
      
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Unknown error occurred'

      const errorMsg: ChatMessage = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: `❌ Error: ${errorMessage}\n\n**Troubleshooting:**\n- Check browser console for details\n- Verify API key in .env.local\n- Make sure Gemini API is enabled\n- Try a simpler question`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="flex-1 flex flex-col relative z-10">
      {/* Header */}
      <header className="border-b border-purple-500/20 backdrop-blur-xl bg-slate-950/40 px-6 py-4 sticky top-0">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              🛡️ Cybersecurity AI
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Powered by Gemini 2.5 • Real-time guidance
            </p>
          </div>
          <div className="text-right">
            <div className="inline-block px-3 py-1 rounded-full bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-500/30 text-xs font-semibold text-purple-300">
              🔒 Secure Chat
            </div>
          </div>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        {isLoading && <LoadingSpinner />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-purple-500/20 backdrop-blur-xl bg-slate-950/40 p-6"
      >
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about XSS, SQL Injection, malware, CVEs, security best practices..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-lg bg-slate-900/60 border border-purple-500/30 text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none transition-all focus:ring-2 focus:ring-purple-500/30 backdrop-blur disabled:opacity-50"
            autoFocus
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 rounded-lg font-semibold text-white bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-purple-500/50 hover:shadow-purple-500/75 flex items-center gap-2"
          >
            <Send size={20} />
            <span className="hidden sm:inline">{isLoading ? 'Thinking...' : 'Send'}</span>
          </button>
        </div>
      </form>
    </div>
  )
}
