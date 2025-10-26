'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  BookOpenIcon, 
  ChatBubbleLeftRightIcon, 
  QuestionMarkCircleIcon,
  HomeIcon 
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Knowledge Base', href: '/knowledge-base', icon: BookOpenIcon },
  { name: 'Q&A Management', href: '/qa-management', icon: QuestionMarkCircleIcon },
  { name: 'AI Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">RAG</span>
              </div>
              <span className="font-semibold text-gray-900">Exercise 6</span>
            </Link>
            
            <div className="hidden md:flex space-x-6">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={clsx(
                      'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    )}
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              Backend: <span className="text-green-600">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
