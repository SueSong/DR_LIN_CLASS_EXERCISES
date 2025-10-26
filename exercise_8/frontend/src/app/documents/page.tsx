"use client";

import { useEffect, useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { api } from "../../lib/api";
import { FileText, Upload, Trash2, Eye, Calendar, FileType } from "lucide-react";

interface Document {
  doc_id: string;
  name: string;
  uploaded_at?: string;
  size?: number;
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      // Mock data - in real implementation, this would call api.listDocs()
      const mockDocs = [
        {
          doc_id: "doc_001",
          name: "SaaS_MSA_v2.pdf",
          uploaded_at: "2025-10-06T10:00:00Z",
          size: 245678,
        },
        {
          doc_id: "doc_002",
          name: "NDA_Template.docx",
          uploaded_at: "2025-10-06T09:30:00Z",
          size: 123456,
        },
        {
          doc_id: "doc_003",
          name: "DPA_GDPR.pdf",
          uploaded_at: "2025-10-06T08:45:00Z",
          size: 345678,
        },
      ];
      setDocs(mockDocs);
      setError(null);
    } catch (err) {
      setError("Failed to load documents");
      console.error(err);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    setUploading(true);
    setError(null);
    
    try {
      // Mock upload - in real implementation, this would call api.uploadDoc(file)
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate upload delay
      
      // Add mock uploaded files to the list
      const newDocs = acceptedFiles.map((file, index) => ({
        doc_id: `doc_${Date.now()}_${index}`,
        name: file.name,
        uploaded_at: new Date().toISOString(),
        size: file.size,
      }));
      
      setDocs(prevDocs => [...newDocs, ...prevDocs]);
      setError(null);
    } catch (err) {
      setError("Failed to upload document");
      console.error(err);
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true,
  });

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "Unknown";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Documents</h1>
        <p className="text-gray-600">
          Upload legal contracts for review. Supported formats: PDF, DOCX, DOC, MD, TXT
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Upload Area */}
      <div className="mb-8">
        <div
          {...getRootProps()}
          className={`card border-2 border-dashed cursor-pointer transition-all ${
            isDragActive
              ? "border-primary-500 bg-primary-50"
              : "border-gray-300 hover:border-primary-400 hover:bg-gray-50"
          } ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <input {...getInputProps()} disabled={uploading} />
          <div className="text-center py-8">
            <Upload
              className={`mx-auto h-12 w-12 mb-4 ${
                isDragActive ? "text-primary-600" : "text-gray-400"
              }`}
            />
            {uploading ? (
              <p className="text-lg text-gray-600">Uploading...</p>
            ) : isDragActive ? (
              <p className="text-lg text-primary-600 font-medium">
                Drop the files here...
              </p>
            ) : (
              <>
                <p className="text-lg text-gray-700 mb-2">
                  Drag & drop documents here, or click to select
                </p>
                <p className="text-sm text-gray-500">
                  Supports PDF, DOCX, DOC, Markdown, and TXT files
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Uploaded Documents ({docs.length})
        </h2>
        
        {docs.length === 0 ? (
          <div className="card text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600">No documents uploaded yet</p>
            <p className="text-sm text-gray-500 mt-2">
              Upload your first document to get started
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {docs.map((doc) => (
              <div
                key={doc.doc_id}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="bg-primary-100 p-3 rounded-lg">
                      <FileText className="w-6 h-6 text-primary-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
                        {doc.name}
                      </h3>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <div className="flex items-center">
                          <FileType className="w-4 h-4 mr-1" />
                          <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                            {doc.doc_id}
                          </span>
                        </div>
                        {doc.uploaded_at && (
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            {formatDate(doc.uploaded_at)}
                          </div>
                        )}
                        {doc.size && (
                          <div className="flex items-center">
                            <FileText className="w-4 h-4 mr-1" />
                            {formatFileSize(doc.size)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="View document"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
