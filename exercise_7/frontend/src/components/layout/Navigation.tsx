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
    <nav className="bg-white border-b">
      <div className="container mx-auto px-4 py-3 flex items-center gap-4">
        <Link href="/" className="font-semibold">RAG Chatbot</Link>
        <div className="flex items-center gap-3 text-sm">
          <Link href="/knowledge-base" className="text-gray-700 hover:text-black">Knowledge Base</Link>
          <Link href="/qa-management" className="text-gray-700 hover:text-black">Q&A</Link>
          <Link href="/chat" className="text-gray-700 hover:text-black">Chat</Link>
          <Link href="/agent-console" className="text-gray-700 hover:text-black">Agent Console</Link>
          <Link href="/prompts" className="text-gray-700 hover:text-black">Prompts</Link>
        </div>
      </div>
    </nav>
  )
}
