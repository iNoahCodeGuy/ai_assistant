'use client'

import { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import type { Message } from '../hooks/useChat'

interface ChatMessagesProps {
  messages: Message[]
  loading: boolean
}

/**
 * Messages container with auto-scroll and loading indicator
 */
export function ChatMessages({ messages, loading }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg mb-2">👋 Hi! I'm Noah's AI assistant.</p>
            <p className="text-gray-500">Ask me anything about Noah's experience, skills, or projects!</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        
        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-chat-primary to-purple-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm">🤔</span>
            </div>
            <div className="bg-chat-surface border border-chat-border rounded-2xl px-6 py-4">
              <div className="flex gap-2">
                <div className="w-2 h-2 rounded-full bg-chat-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full bg-chat-primary animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-chat-primary animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
