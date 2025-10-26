'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  PlusIcon, 
  QuestionMarkCircleIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'
import { QAForm } from '@/components/qa-management/QAForm'
import { QAList } from '@/components/qa-management/QAList'
import { api, QAPair } from '@/lib/api'

export default function QAManagementPage() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingQA, setEditingQA] = useState<QAPair | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  const queryClient = useQueryClient()

  // Fetch Q&A pairs
  const { data: qaPairs, isLoading, error } = useQuery({
    queryKey: ['qa-pairs'],
    queryFn: api.getQAPairs,
  })

  // Create mutation
  const createMutation = useMutation({
    mutationFn: api.createQAPair,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qa-pairs'] })
      setIsFormOpen(false)
    },
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<QAPair> }) =>
      api.updateQAPair(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qa-pairs'] })
      setEditingQA(null)
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: api.deleteQAPair,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qa-pairs'] })
    },
  })

  const handleCreate = (data: { question: string; answer: string; tags?: string[] }) => {
    createMutation.mutate(data)
  }

  const handleUpdate = (data: { question: string; answer: string; tags?: string[] }) => {
    if (editingQA) {
      updateMutation.mutate({
        id: editingQA.id,
        data,
      })
    }
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this Q&A pair?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleEdit = (qa: QAPair) => {
    setEditingQA(qa)
    setIsFormOpen(true)
  }

  const handleCloseForm = () => {
    setIsFormOpen(false)
    setEditingQA(null)
  }

  // Filter Q&A pairs based on search term
  const filteredQAPairs = qaPairs?.filter(qa =>
    qa.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    qa.answer.toLowerCase().includes(searchTerm.toLowerCase()) ||
    qa.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || []

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Q&A Management</h1>
          <p className="mt-2 text-gray-600">
            Create and manage question-answer pairs for direct matching in the RAG system
          </p>
        </div>
        <button
          onClick={() => setIsFormOpen(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          Add Q&A Pair
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search questions, answers, or tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <QuestionMarkCircleIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Q&A Pairs</p>
              <p className="text-2xl font-semibold text-gray-900">
                {qaPairs?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <MagnifyingGlassIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Filtered Results</p>
              <p className="text-2xl font-semibold text-gray-900">
                {filteredQAPairs.length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <PlusIcon className="h-8 w-8 text-purple-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recently Added</p>
              <p className="text-2xl font-semibold text-gray-900">
                {qaPairs?.filter(qa => {
                  const dayAgo = new Date()
                  dayAgo.setDate(dayAgo.getDate() - 1)
                  return new Date(qa.created_at) > dayAgo
                }).length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Q&A List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Q&A Pairs
            {searchTerm && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                - Showing {filteredQAPairs.length} results for "{searchTerm}"
              </span>
            )}
          </h2>
        </div>
        <div className="p-6">
          <QAList
            qaPairs={filteredQAPairs}
            onEdit={handleEdit}
            onDelete={handleDelete}
            isLoading={isLoading}
            error={error}
            isDeleting={deleteMutation.isPending}
          />
        </div>
      </div>

      {/* Q&A Form Modal */}
      {isFormOpen && (
        <QAForm
          qa={editingQA}
          onSubmit={editingQA ? handleUpdate : handleCreate}
          onClose={handleCloseForm}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      )}
    </div>
  )
}
