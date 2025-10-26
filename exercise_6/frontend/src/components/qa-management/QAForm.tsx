'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { QAPair } from '@/lib/api'

interface QAFormProps {
  qa?: QAPair | null
  onSubmit: (data: { question: string; answer: string; tags?: string[] }) => void
  onClose: () => void
  isLoading: boolean
}

export function QAForm({ qa, onSubmit, onClose, isLoading }: QAFormProps) {
  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    tags: '',
  })

  useEffect(() => {
    if (qa) {
      setFormData({
        question: qa.question,
        answer: qa.answer,
        tags: qa.tags?.join(', ') || '',
      })
    }
  }, [qa])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const tags = formData.tags
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)

    onSubmit({
      question: formData.question.trim(),
      answer: formData.answer.trim(),
      tags: tags.length > 0 ? tags : undefined,
    })
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {qa ? 'Edit Q&A Pair' : 'Add New Q&A Pair'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Question */}
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Question *
            </label>
            <textarea
              id="question"
              rows={3}
              value={formData.question}
              onChange={(e) => handleChange('question', e.target.value)}
              className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter the question that users might ask..."
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Write the question as users would naturally ask it
            </p>
          </div>

          {/* Answer */}
          <div>
            <label htmlFor="answer" className="block text-sm font-medium text-gray-700 mb-2">
              Answer *
            </label>
            <textarea
              id="answer"
              rows={6}
              value={formData.answer}
              onChange={(e) => handleChange('answer', e.target.value)}
              className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter the detailed answer..."
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Provide a comprehensive answer that addresses the question
            </p>
          </div>

          {/* Tags */}
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
              Tags (Optional)
            </label>
            <input
              type="text"
              id="tags"
              value={formData.tags}
              onChange={(e) => handleChange('tags', e.target.value)}
              className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="tag1, tag2, tag3"
            />
            <p className="mt-1 text-xs text-gray-500">
              Separate multiple tags with commas. Tags help with categorization and search.
            </p>
          </div>

          {/* Character Counts */}
          <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
            <div>
              Question: {formData.question.length} characters
            </div>
            <div>
              Answer: {formData.answer.length} characters
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading || !formData.question.trim() || !formData.answer.trim()}
            >
              {isLoading ? 'Saving...' : qa ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
