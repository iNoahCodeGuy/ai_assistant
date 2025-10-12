'use client'

import { Send } from 'lucide-react'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  disabled: boolean
}

/**
 * Chat input component with send button
 * Handles form submission and validation
 */
export function ChatInput({ value, onChange, onSubmit, disabled }: ChatInputProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSubmit()
  }

  return (
    <div className="border-t border-chat-border bg-chat-surface/80 backdrop-blur-lg">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Ask me anything about Noah..."
            className="flex-1 bg-chat-bg border border-chat-border rounded-xl px-6 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-chat-primary transition-colors"
            disabled={disabled}
          />
          <button
            type="submit"
            disabled={!value.trim() || disabled}
            className="bg-gradient-to-r from-chat-primary to-purple-600 text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg hover:shadow-chat-primary/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  )
}
