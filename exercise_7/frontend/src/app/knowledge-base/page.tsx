'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  DocumentPlusIcon, 
  TrashIcon, 
  DocumentTextIcon,
  CloudArrowUpIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { DocumentArrowUpIcon } from '@heroicons/react/24/solid'
import { FileUpload } from '@/components/knowledge-base/FileUpload'
import { DocumentList } from '@/components/knowledge-base/DocumentList'
import { api } from '@/lib/api'

export default function KnowledgeBasePage() {
  const [uploadStatus, setUploadStatus] = useState<{
    isUploading: boolean
    progress: number
    message: string
  }>({
    isUploading: false,
    progress: 0,
    message: ''
  })

  const queryClient = useQueryClient()

  // Fetch documents
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: api.getDocuments,
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: api.uploadDocument,
    onMutate: () => {
      setUploadStatus({
        isUploading: true,
        progress: 0,
        message: 'Starting upload...'
      })
    },
    onSuccess: (data) => {
      setUploadStatus({
        isUploading: false,
        progress: 100,
        message: `Successfully uploaded: ${data.filename}`
      })
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      // Clear message after 3 seconds
      setTimeout(() => {
        setUploadStatus(prev => ({ ...prev, message: '' }))
      }, 3000)
    },
    onError: (error: any) => {
      setUploadStatus({
        isUploading: false,
        progress: 0,
        message: `Upload failed: ${error.response?.data?.message || error.message}`
      })
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: api.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const handleFileUpload = (files: File[]) => {
    files.forEach(file => {
      uploadMutation.mutate(file)
    })
  }

  const handleDeleteDocument = (id: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-2 text-gray-600">
          Upload and manage documents for the RAG system. Supported formats: PDF, TXT
        </p>
      </div>

      {/* Upload Status */}
      {uploadStatus.message && (
        <div className={`rounded-md p-4 ${
          uploadStatus.message.includes('failed') 
            ? 'bg-red-50 border border-red-200' 
            : 'bg-green-50 border border-green-200'
        }`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {uploadStatus.message.includes('failed') ? (
                <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
              ) : (
                <DocumentArrowUpIcon className="h-5 w-5 text-green-400" />
              )}
            </div>
            <div className="ml-3">
              <p className={`text-sm font-medium ${
                uploadStatus.message.includes('failed') ? 'text-red-800' : 'text-green-800'
              }`}>
                {uploadStatus.message}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <DocumentPlusIcon className="w-5 h-5 mr-2" />
            Upload Documents
          </h2>
        </div>
        <div className="p-6">
          <FileUpload
            onFilesSelected={handleFileUpload}
            isUploading={uploadStatus.isUploading}
            progress={uploadStatus.progress}
          />
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <DocumentTextIcon className="w-5 h-5 mr-2" />
            Uploaded Documents
            {documents && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({documents.length} documents)
              </span>
            )}
          </h2>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gray-200 rounded"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading documents</h3>
              <p className="mt-1 text-sm text-gray-500">
                {error instanceof Error ? error.message : 'Failed to load documents'}
              </p>
            </div>
          ) : !documents || documents.length === 0 ? (
            <div className="text-center py-8">
              <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No documents uploaded</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by uploading your first document above.
              </p>
            </div>
          ) : (
            <DocumentList
              documents={documents}
              onDelete={handleDeleteDocument}
              isDeleting={deleteMutation.isPending}
            />
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Documents</p>
              <p className="text-2xl font-semibold text-gray-900">
                {documents?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentPlusIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Processing</p>
              <p className="text-2xl font-semibold text-gray-900">
                {documents?.filter(doc => doc.status === 'processing').length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CloudArrowUpIcon className="h-8 w-8 text-purple-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Ready</p>
              <p className="text-2xl font-semibold text-gray-900">
                {documents?.filter(doc => doc.status === 'processed').length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
