'use client'

import { useQuery } from '@tanstack/react-query'
import { 
  BookOpenIcon, 
  ChatBubbleLeftRightIcon, 
  QuestionMarkCircleIcon,
  ServerIcon,
  CircleStackIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import { api, apiClient } from '@/lib/api'

export default function Dashboard() {
  const { data: healthData, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.get('/health/detailed'),
  })

  // Fetch documents count
  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: api.getDocuments,
  })

  // Fetch Q&A pairs count
  const { data: qaPairs, isLoading: qaPairsLoading } = useQuery({
    queryKey: ['qa-pairs'],
    queryFn: api.getQAPairs,
  })

  const stats = [
    {
      name: 'Knowledge Base',
      value: documentsLoading ? 'Loading...' : `${documents?.length || 0} documents`,
      icon: BookOpenIcon,
      href: '/knowledge-base',
      color: 'bg-blue-500',
    },
    {
      name: 'Q&A Pairs',
      value: qaPairsLoading ? 'Loading...' : `${qaPairs?.length || 0} pairs`,
      icon: QuestionMarkCircleIcon,
      href: '/qa-management',
      color: 'bg-green-500',
    },
    {
      name: 'Chat Sessions',
      value: '0 active',
      icon: ChatBubbleLeftRightIcon,
      href: '/chat',
      color: 'bg-purple-500',
    },
  ]

  const services = [
    {
      name: 'Backend API',
      status: healthData?.status || 'unknown',
      icon: ServerIcon,
      details: healthData ? `Version ${healthData.version}` : 'Loading...',
    },
    {
      name: 'PostgreSQL',
      status: healthData?.dependencies?.database?.status || 'unknown',
      icon: CircleStackIcon,
      details: 'Vector Database',
    },
    {
      name: 'ChromaDB',
      status: healthData?.dependencies?.chromadb?.status || 'unknown',
      icon: CpuChipIcon,
      details: 'Vector Store',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">RAG Chatbot Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Manage your knowledge base, Q&A pairs, and interact with the AI assistant
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            href={stat.href}
            className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center">
              <div className={`${stat.color} rounded-lg p-3`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {services.map((service) => (
                <div key={service.name} className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                    <service.icon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium text-gray-900">{service.name}</h3>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          service.status === 'healthy'
                            ? 'bg-green-100 text-green-800'
                            : service.status === 'degraded'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {service.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{service.details}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/knowledge-base"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <BookOpenIcon className="w-8 h-8 text-blue-500" />
              <div className="ml-3">
                <p className="font-medium text-gray-900">Upload Documents</p>
                <p className="text-sm text-gray-600">Add PDFs or text files</p>
              </div>
            </Link>
            
            <Link
              href="/qa-management"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <QuestionMarkCircleIcon className="w-8 h-8 text-green-500" />
              <div className="ml-3">
                <p className="font-medium text-gray-900">Add Q&A Pairs</p>
                <p className="text-sm text-gray-600">Create question-answer pairs</p>
              </div>
            </Link>
            
            <Link
              href="/chat"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-purple-500" />
              <div className="ml-3">
                <p className="font-medium text-gray-900">Start Chatting</p>
                <p className="text-sm text-gray-600">Ask questions to the AI</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}