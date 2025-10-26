'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { 
  CloudArrowUpIcon, 
  DocumentTextIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void
  isUploading: boolean
  progress: number
}

export function FileUpload({ onFilesSelected, isUploading, progress }: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      alert(`Some files were rejected. Please upload only PDF or TXT files under 50MB.`)
    }
    
    if (acceptedFiles.length > 0) {
      onFilesSelected(acceptedFiles)
    }
  }, [onFilesSelected])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
    disabled: isUploading,
  })

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive && !isDragReject && 'border-blue-400 bg-blue-50',
          isDragReject && 'border-red-400 bg-red-50',
          !isDragActive && !isDragReject && 'border-gray-300 hover:border-gray-400',
          isUploading && 'cursor-not-allowed opacity-50'
        )}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          {isDragReject ? (
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
          ) : (
            <CloudArrowUpIcon className={clsx(
              'mx-auto h-12 w-12',
              isDragActive ? 'text-blue-500' : 'text-gray-400'
            )} />
          )}
          
          <div>
            {isDragReject ? (
              <p className="text-red-600 font-medium">
                Invalid file type. Please upload PDF or TXT files only.
              </p>
            ) : isDragActive ? (
              <p className="text-blue-600 font-medium">
                Drop the files here...
              </p>
            ) : (
              <div>
                <p className="text-gray-600 font-medium">
                  {isUploading ? 'Uploading...' : 'Drop files here or click to browse'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Supports PDF, TXT, and MD files up to 50MB each
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Uploading...</span>
            <span className="text-gray-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* File Type Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Supported File Types:</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="w-4 h-4 text-red-500" />
            <span className="text-gray-600">PDF Documents</span>
          </div>
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="w-4 h-4 text-blue-500" />
            <span className="text-gray-600">Text Files (.txt)</span>
          </div>
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="w-4 h-4 text-green-500" />
            <span className="text-gray-600">Markdown (.md)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
