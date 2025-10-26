'use client'

import { 
  DocumentTextIcon, 
  TrashIcon, 
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

interface Document {
  id: string
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  status: 'processing' | 'completed' | 'failed'
  title?: string
  created_at: string
  updated_at: string
}

interface DocumentListProps {
  documents: Document[]
  onDelete: (id: string) => void
  isDeleting: boolean
}

export function DocumentList({ documents, onDelete, isDeleting }: DocumentListProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />
      case 'failed':
        return <ExclamationCircleIcon className="w-5 h-5 text-red-500" />
      default:
        return <DocumentTextIcon className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    
    switch (status) {
      case 'processing':
        return `${baseClasses} bg-yellow-100 text-yellow-800`
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`
    }
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-8">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
        <p className="mt-1 text-sm text-gray-500">
          Upload your first document to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {documents.map((document) => (
        <div
          key={document.id}
          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-4 flex-1">
            <div className="flex-shrink-0">
              {getStatusIcon(document.status)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {document.title || document.original_filename}
                </p>
                <span className={getStatusBadge(document.status)}>
                  {document.status}
                </span>
              </div>
              
              <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                <span>{formatFileSize(document.file_size)}</span>
                <span className="capitalize">{document.file_type}</span>
                <span>Uploaded {formatDate(document.created_at)}</span>
              </div>
              
              {document.status === 'failed' && (
                <p className="text-sm text-red-600 mt-1">
                  Processing failed. Please try uploading again.
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onDelete(document.id)}
              disabled={isDeleting}
              className={clsx(
                "p-2 text-gray-400 hover:text-red-600 transition-colors",
                isDeleting && "opacity-50 cursor-not-allowed"
              )}
              title="Delete document"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
