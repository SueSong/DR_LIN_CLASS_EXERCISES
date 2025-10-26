"use client";

import { useState, useEffect } from "react";
import { uploadDocument, listDocuments, getDocument } from "@/lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error("Failed to load documents:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const file = formData.get("file") as File;

    if (!file) return;

    setUploading(true);
    try {
      await uploadDocument(file);
      await loadDocuments();
      (e.target as HTMLFormElement).reset();
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  const handleViewDocument = async (docId: string) => {
    try {
      const doc = await getDocument(docId);
      setSelectedDoc(doc);
    } catch (error) {
      console.error("Failed to load document:", error);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Documents</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            Upload Document
          </h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Legal Document
              </label>
              <input
                type="file"
                name="file"
                accept=".txt,.md,.doc,.docx"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Supported formats: .txt, .md, .doc, .docx
              </p>
            </div>
            <button
              type="submit"
              disabled={uploading}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {uploading ? "Uploading..." : "Upload Document"}
            </button>
          </form>
        </div>

        {/* Document List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            Uploaded Documents
          </h2>
          {loading ? (
            <p className="text-gray-600">Loading documents...</p>
          ) : documents.length === 0 ? (
            <p className="text-gray-600">No documents uploaded yet.</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {documents.map((doc) => (
                <div
                  key={doc.doc_id}
                  className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 cursor-pointer"
                  onClick={() => handleViewDocument(doc.doc_id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-800">{doc.name}</h3>
                      <p className="text-sm text-gray-500">
                        Uploaded: {new Date(doc.uploaded_at).toLocaleString()}
                      </p>
                      {doc.metadata && (
                        <p className="text-xs text-gray-500">
                          Size: {doc.metadata.size} bytes | Lines: {doc.metadata.lines}
                        </p>
                      )}
                    </div>
                    <span className="text-xs text-blue-600 font-medium">
                      View →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Document Preview */}
      {selectedDoc && (
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">
              Document Preview: {selectedDoc.name}
            </h2>
            <button
              onClick={() => setSelectedDoc(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕ Close
            </button>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
              {selectedDoc.content}
            </pre>
          </div>
          <div className="mt-4">
            <a
              href={`/review?doc_id=${selectedDoc.doc_id || Object.keys(documents).find(k => documents[k] === selectedDoc)}`}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 inline-block"
            >
              Start Review Process →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

