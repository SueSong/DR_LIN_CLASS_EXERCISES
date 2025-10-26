'use client'

import { 
  PencilIcon, 
  TrashIcon, 
  QuestionMarkCircleIcon,
  ExclamationTriangleIcon,
  TagIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { QAPair } from '@/lib/api'

interface QAListProps {
  qaPairs: QAPair[]
  onEdit: (qa: QAPair) => void
  onDelete: (id: string) => void
  isLoading: boolean
  error: any
  isDeleting: boolean
}

export function QAList({ qaPairs, onEdit, onDelete, isLoading, error, isDeleting }: QAListProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="border border-gray-200 rounded-lg p-6">
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
              <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              <div className="flex space-x-2">
                <div className="h-6 bg-gray-200 rounded w-16"></div>
                <div className="h-6 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading Q&A pairs</h3>
        <p className="mt-1 text-sm text-gray-500">
          {error instanceof Error ? error.message : 'Failed to load Q&A pairs'}
        </p>
      </div>
    )
  }

  if (qaPairs.length === 0) {
    return (
      <div className="text-center py-8">
        <QuestionMarkCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No Q&A pairs found</h3>
        <p className="mt-1 text-sm text-gray-500">
          Create your first Q&A pair to get started with direct question matching.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {qaPairs.map((qa) => (
        <div
          key={qa.id}
          className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
        >
          <div className="space-y-4">
            {/* Question */}
            <div>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Q: {qa.question}
                  </h3>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => onEdit(qa)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Edit Q&A pair"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(qa.id)}
                    disabled={isDeleting}
                    className={clsx(
                      "p-2 text-gray-400 hover:text-red-600 transition-colors",
                      isDeleting && "opacity-50 cursor-not-allowed"
                    )}
                    title="Delete Q&A pair"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Answer */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">A:</p>
              <p className="text-gray-900 whitespace-pre-wrap">{qa.answer}</p>
            </div>

            {/* Tags and Metadata */}
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center space-x-4">
                {qa.tags && qa.tags.length > 0 && (
                  <div className="flex items-center space-x-2">
                    <TagIcon className="w-4 h-4" />
                    <div className="flex flex-wrap gap-1">
                      {qa.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-4">
                <span>Created: {formatDate(qa.created_at)}</span>
                {qa.updated_at !== qa.created_at && (
                  <span>Updated: {formatDate(qa.updated_at)}</span>
                )}
              </div>
            </div>

            {/* Character counts */}
            <div className="flex justify-between text-xs text-gray-400 pt-2 border-t border-gray-100">
              <span>Question: {qa.question.length} chars</span>
              <span>Answer: {qa.answer.length} chars</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
