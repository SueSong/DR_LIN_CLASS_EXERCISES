'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { 
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { SourcesPanel } from '@/components/chat/SourcesPanel'
import { api, ChatMessage as ChatMessageType } from '@/lib/api'

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) => api.sendMessage(message, sessionId),
    onSuccess: (response) => {
      // Add user message
      const userMessage: ChatMessageType = {
        id: `user_${Date.now()}`,
        type: 'user',
        content: inputMessage,
        timestamp: new Date().toISOString(),
      }

      // Add assistant message with sources (adapt backend response to frontend format)
      const assistantMessage: ChatMessageType = {
        id: `assistant_${Date.now()}`,
        type: 'assistant',
        content: response.response, // Backend uses 'response' field
        timestamp: new Date().toISOString(),
        sources: {
          knowledge_base_hits: response.sources?.map(source => ({
            id: source.document_id,
            content: source.chunk_text,
            filename: source.filename,
            similarity_score: source.similarity_score,
          })) || [],
          qa_hits: response.qa_matches?.map(qa => ({
            id: `qa_${Date.now()}_${Math.random()}`,
            question: qa.question,
            answer: qa.answer,
            similarity_score: qa.similarity_score,
          })) || [],
        },
      }

      setMessages(prev => [...prev, userMessage, assistantMessage])
      setInputMessage('')
    },
    onError: (error: any) => {
      // Add user message
      const userMessage: ChatMessageType = {
        id: `user_${Date.now()}`,
        type: 'user',
        content: inputMessage,
        timestamp: new Date().toISOString(),
      }

      // Add error message
      const errorMessage: ChatMessageType = {
        id: `error_${Date.now()}`,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.message || error.message}`,
        timestamp: new Date().toISOString(),
      }

      setMessages(prev => [...prev, userMessage, errorMessage])
      setInputMessage('')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputMessage.trim() && !sendMessageMutation.isPending) {
      sendMessageMutation.mutate(inputMessage.trim())
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <div className="flex items-center space-x-3">
          <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Chat Assistant</h1>
            <p className="text-gray-600">
              Ask questions about your knowledge base. I'll search through documents and Q&A pairs to provide accurate answers.
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex space-x-6 min-h-0">
        {/* Chat Area */}
        <div className="flex-1 bg-white rounded-lg shadow flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Start a conversation</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Ask me anything about your uploaded documents or Q&A pairs.
                </p>
                <div className="mt-6 space-y-2">
                  <p className="text-xs text-gray-400">Try asking:</p>
                  <div className="space-y-1 text-xs text-blue-600">
                    <p>"What is the main topic of the uploaded documents?"</p>
                    <p>"Can you summarize the key points?"</p>
                    <p>"How does X relate to Y?"</p>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))
            )}
            
            {sendMessageMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about your knowledge base..."
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  rows={2}
                  disabled={sendMessageMutation.isPending}
                />
              </div>
              <button
                type="submit"
                disabled={!inputMessage.trim() || sendMessageMutation.isPending}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PaperAirplaneIcon className="w-4 h-4" />
              </button>
            </form>
            <p className="mt-2 text-xs text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>

        {/* Sources Panel */}
        <div className="w-80 bg-white rounded-lg shadow">
          <SourcesPanel 
            sources={messages.length > 0 ? messages[messages.length - 1]?.sources : undefined}
          />
        </div>
      </div>
    </div>
  )
}
