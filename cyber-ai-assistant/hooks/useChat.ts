'use client'

import { useState, useCallback } from 'react'
import { callAskAPI, ChatMessage, APIResponse } from '@/lib/api'

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(
    async (content: string, mode: 'beginner' | 'advanced'): Promise<APIResponse | null> => {
      setIsLoading(true)

      try {
        // Add user message
        const userMsg: ChatMessage = {
          id: Date.now().toString(),
          role: 'user',
          content,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, userMsg])

        // Call API
        const response = await callAskAPI({
          question: content,
          mode,
          detectTopic: true,
          userId: 'anonymous',
        })

        // Add assistant message
        const assistantMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.answer,
          timestamp: new Date(),
          metadata: response.data,
        }
        setMessages((prev) => [...prev, assistantMsg])

        return response
      } catch (error) {
        console.error('Chat error:', error)
        const errorMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '❌ Error processing your request. Please try again.',
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, errorMsg])
        return null
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  return { messages, isLoading, sendMessage }
}
