import Link from 'next/link'
import { PhoneCall, Users, BarChart3, Settings } from 'lucide-react'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🎧 AI Call Center Assistant
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Real-time AI-powered assistance for call center agents with live transcription,
            customer insights, and intelligent suggestions.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <FeatureCard
            icon={<PhoneCall className="w-8 h-8" />}
            title="Live Calls"
            description="Handle customer calls with real-time AI assistance"
            href="/calls"
            color="bg-blue-500"
          />
          <FeatureCard
            icon={<Users className="w-8 h-8" />}
            title="Customers"
            description="Search and view customer information"
            href="/customers"
            color="bg-green-500"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="Analytics"
            description="View call metrics and performance"
            href="/analytics"
            color="bg-purple-500"
          />
          <FeatureCard
            icon={<Settings className="w-8 h-8" />}
            title="Settings"
            description="Configure your workspace"
            href="/settings"
            color="bg-gray-500"
          />
        </div>

        {/* Quick Start */}
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            🚀 Quick Start
          </h2>
          <ol className="space-y-4 text-gray-700">
            <li className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold mr-3">
                1
              </span>
              <div>
                <strong>Login:</strong> Use your credentials (default: agent1 / agent123)
              </div>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold mr-3">
                2
              </span>
              <div>
                <strong>Start a call:</strong> Click "New Call" to begin a customer conversation
              </div>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold mr-3">
                3
              </span>
              <div>
                <strong>Get AI assistance:</strong> See real-time transcription and AI suggestions
              </div>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold mr-3">
                4
              </span>
              <div>
                <strong>View customer info:</strong> Automatically loaded customer history and orders
              </div>
            </li>
          </ol>

          <div className="mt-8 flex gap-4">
            <Link
              href="/auth/signin"
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-center hover:bg-blue-700 transition"
            >
              Sign In
            </Link>
            <Link
              href="/demo"
              className="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold text-center hover:bg-gray-300 transition"
            >
              View Demo
            </Link>
          </div>
        </div>

        {/* Features List */}
        <div className="mt-12 grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">
              ✨ Key Features
            </h3>
            <ul className="space-y-2 text-gray-700">
              <li>• Real-time audio streaming (WebRTC)</li>
              <li>• Live speech-to-text transcription</li>
              <li>• Streaming AI suggestions</li>
              <li>• Automatic customer lookup</li>
              <li>• Order and ticket history</li>
              <li>• Sentiment analysis</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">
              🎓 Learning Objectives
            </h3>
            <ul className="space-y-2 text-gray-700">
              <li>• WebRTC audio streaming</li>
              <li>• Server-Sent Events (SSE)</li>
              <li>• WebSocket communication</li>
              <li>• Optimistic UI patterns</li>
              <li>• Session management</li>
              <li>• Role-based authentication</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  )
}

function FeatureCard({ icon, title, description, href, color }: {
  icon: React.ReactNode
  title: string
  description: string
  href: string
  color: string
}) {
  return (
    <Link href={href}>
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow cursor-pointer h-full">
        <div className={`${color} w-14 h-14 rounded-lg flex items-center justify-center text-white mb-4`}>
          {icon}
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
    </Link>
  )
}

