'use client'

import { 
  UserIcon, 
  CpuChipIcon,
  DocumentTextIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'
import ReactMarkdown from 'react-markdown'
import { ChatMessage as ChatMessageType } from '@/lib/api'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === 'user'
  
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex space-x-3 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-gray-500'
        }`}>
          {isUser ? (
            <UserIcon className="w-5 h-5 text-white" />
          ) : (
            <CpuChipIcon className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
          <div className={`inline-block rounded-lg px-4 py-2 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-900'
          }`}>
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
          
          {/* Sources Summary for Assistant Messages */}
          {!isUser && message.sources && (
            <div className="mt-2 text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                {message.sources.knowledge_base_hits && message.sources.knowledge_base_hits.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <DocumentTextIcon className="w-3 h-3" />
                    <span>{message.sources.knowledge_base_hits.length} document(s)</span>
                  </div>
                )}
                {message.sources.qa_hits && message.sources.qa_hits.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <QuestionMarkCircleIcon className="w-3 h-3" />
                    <span>{message.sources.qa_hits.length} Q&A pair(s)</span>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Timestamp */}
          <div className={`mt-1 text-xs text-gray-500 ${isUser ? 'text-right' : ''}`}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    </div>
  )
}
