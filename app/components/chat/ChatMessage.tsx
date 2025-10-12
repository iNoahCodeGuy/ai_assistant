'use client'

import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { Message } from '../hooks/useChat'

interface ChatMessageProps {
  message: Message
}

/**
 * Individual message bubble component
 * Handles user/assistant styling and source display
 */
export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-chat-primary to-purple-600 flex items-center justify-center flex-shrink-0">
          <Bot size={20} className="text-white" />
        </div>
      )}
      
      <div className={`max-w-2xl rounded-2xl px-6 py-4 ${
        isUser 
          ? 'bg-gradient-to-r from-chat-primary to-purple-600 text-white' 
          : 'bg-chat-surface border border-chat-border'
      }`}>
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown
              components={{
                pre: ({ children }) => (
                  <pre className="bg-chat-bg rounded-lg p-4 overflow-x-auto my-3">
                    {children}
                  </pre>
                ),
                code: ({ children }) => (
                  <code className="bg-chat-bg px-2 py-1 rounded text-sm">
                    {children}
                  </code>
                ),
                a: ({ children, href }) => (
                  <a 
                    href={href} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-chat-primary hover:underline"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-chat-border/30">
            <p className="text-xs text-gray-400 mb-2">Sources:</p>
            <div className="space-y-1">
              {message.sources.map((source, idx) => (
                <div key={idx} className="text-xs text-gray-400 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-chat-primary" />
                  {source.title} (relevance: {(source.score * 100).toFixed(0)}%)
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
          <User size={20} className="text-gray-300" />
        </div>
      )}
    </div>
  )
}
