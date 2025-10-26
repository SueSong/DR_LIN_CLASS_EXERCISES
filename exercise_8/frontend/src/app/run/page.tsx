"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { Play, FileText, BookOpen, Users, CheckCircle, AlertCircle } from "lucide-react";

interface Document {
  doc_id: string;
  name: string;
}

interface Playbook {
  playbook_id: string;
  name: string;
}

const agentPaths = [
  {
    value: "manager_worker",
    label: "Manager–Worker",
    description: "Task decomposition with parallel workers for clause parsing and risk tagging",
    icon: Users,
    color: "bg-blue-500",
  },
  {
    value: "planner_executor",
    label: "Planner–Executor",
    description: "Multi-step sequential plan with replayable state and checkpoints",
    icon: CheckCircle,
    color: "bg-green-500",
  },
  {
    value: "reviewer_referee",
    label: "Reviewer/Referee",
    description: "Checklist-driven review with referee arbitration for contested clauses",
    icon: AlertCircle,
    color: "bg-orange-500",
  },
];

export default function RunPage() {
  const router = useRouter();
  const [docs, setDocs] = useState<Document[]>([]);
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [docId, setDocId] = useState<string>("");
  const [agentPath, setAgentPath] = useState<string>("manager_worker");
  const [playbookId, setPlaybookId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Mock data - in real implementation, this would call api.listDocs() and api.listPlaybooks()
    setDocs([
      { doc_id: "doc_001", name: "SaaS_MSA_v2.pdf" },
      { doc_id: "doc_002", name: "NDA_Template.docx" },
      { doc_id: "doc_003", name: "DPA_GDPR.pdf" },
    ]);
    setPlaybooks([
      { playbook_id: "playbook_001", name: "Standard SaaS MSA Policy" },
      { playbook_id: "playbook_002", name: "GDPR DPA Policy" },
    ]);
  }, []);

  const handleStartRun = async () => {
    if (!docId) {
      setError("Please select a document");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Mock response - in real implementation, this would call api.run()
      const mockRunId = `run_${Date.now()}`;
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      // Navigate to the run detail page
      router.push(`/run/${mockRunId}`);
    } catch (err) {
      setError("Failed to start run");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectedPath = agentPaths.find((p) => p.value === agentPath);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Start Review</h1>
        <p className="text-gray-600">
          Configure and initiate a multi-agent document review workflow
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* Document Selection */}
        <div className="card">
          <div className="flex items-center mb-4">
            <FileText className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Select Document
            </h2>
          </div>
          {docs.length === 0 ? (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-600 mb-2">No documents available</p>
              <p className="text-sm text-gray-500">
                Please upload a document first
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              {docs.map((doc) => (
                <label
                  key={doc.doc_id}
                  className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    docId === doc.doc_id
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-primary-300 hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="radio"
                    name="document"
                    value={doc.doc_id}
                    checked={docId === doc.doc_id}
                    onChange={(e) => setDocId(e.target.value)}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{doc.name}</p>
                    <p className="text-xs text-gray-500 font-mono mt-1">
                      {doc.doc_id}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Agent Path Selection */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Users className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Select Agent Path
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {agentPaths.map((path) => {
              const Icon = path.icon;
              return (
                <label
                  key={path.value}
                  className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    agentPath === path.value
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-primary-300 hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="radio"
                    name="agentPath"
                    value={path.value}
                    checked={agentPath === path.value}
                    onChange={(e) => setAgentPath(e.target.value)}
                    className="mt-1 mr-3"
                  />
                  <div className={`${path.color} p-2 rounded-lg mr-3`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{path.label}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {path.description}
                    </p>
                  </div>
                </label>
              );
            })}
          </div>
        </div>

        {/* Playbook Selection */}
        <div className="card">
          <div className="flex items-center mb-4">
            <BookOpen className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Select Playbook (Optional)
            </h2>
          </div>
          {playbooks.length === 0 ? (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-600 mb-2">No playbooks available</p>
              <p className="text-sm text-gray-500">
                You can proceed without a playbook or create one first
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              <label
                className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  playbookId === ""
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-200 hover:border-primary-300 hover:bg-gray-50"
                }`}
              >
                <input
                  type="radio"
                  name="playbook"
                  value=""
                  checked={playbookId === ""}
                  onChange={(e) => setPlaybookId(e.target.value)}
                  className="mr-3"
                />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">No Playbook</p>
                  <p className="text-sm text-gray-600 mt-1">
                    Use default review settings
                  </p>
                </div>
              </label>
              {playbooks.map((playbook) => (
                <label
                  key={playbook.playbook_id}
                  className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    playbookId === playbook.playbook_id
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-primary-300 hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="radio"
                    name="playbook"
                    value={playbook.playbook_id}
                    checked={playbookId === playbook.playbook_id}
                    onChange={(e) => setPlaybookId(e.target.value)}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{playbook.name}</p>
                    <p className="text-xs text-gray-500 font-mono mt-1">
                      {playbook.playbook_id}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Summary and Start Button */}
        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Review Configuration
          </h3>
          <div className="space-y-2 text-sm text-gray-700 mb-4">
            <div className="flex items-center">
              <FileText className="w-4 h-4 mr-2 text-primary-600" />
              <strong className="mr-2">Document:</strong>
              {docId
                ? docs.find((d) => d.doc_id === docId)?.name
                : "Not selected"}
            </div>
            <div className="flex items-center">
              <Users className="w-4 h-4 mr-2 text-primary-600" />
              <strong className="mr-2">Agent Path:</strong>
              {selectedPath?.label}
            </div>
            <div className="flex items-center">
              <BookOpen className="w-4 h-4 mr-2 text-primary-600" />
              <strong className="mr-2">Playbook:</strong>
              {playbookId
                ? playbooks.find((p) => p.playbook_id === playbookId)?.name
                : "None"}
            </div>
          </div>
          <button
            onClick={handleStartRun}
            disabled={loading || !docId}
            className="btn-primary w-full flex items-center justify-center text-lg py-3"
          >
            <Play className="w-5 h-5 mr-2" />
            {loading ? "Starting Review..." : "Start Review"}
          </button>
        </div>
      </div>
    </div>
  );
}
