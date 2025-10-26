"use client";

import { useState } from "react";
import Link from "next/link";
import {
  RotateCcw,
  Play,
  Edit,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Users,
  FileText,
  Search,
  Zap,
  Settings,
  Eye,
  Copy,
} from "lucide-react";

// Mock data for demonstration
const mockRuns = [
  {
    run_id: "run_abc123",
    doc_name: "SaaS_MSA_v2.pdf",
    agent_path: "manager_worker",
    score: 92,
    status: "completed",
    timestamp: "2025-10-06T10:23:45Z",
    total_steps: 8,
  },
  {
    run_id: "run_def456",
    doc_name: "NDA_Template.docx",
    agent_path: "planner_executor",
    score: 88,
    status: "completed",
    timestamp: "2025-10-06T09:15:22Z",
    total_steps: 12,
  },
  {
    run_id: "run_ghi789",
    doc_name: "DPA_GDPR.pdf",
    agent_path: "reviewer_referee",
    score: 85,
    status: "completed",
    timestamp: "2025-10-06T08:42:11Z",
    total_steps: 15,
  },
];

const mockTraceDetails = {
  run_id: "run_abc123",
  doc_id: "doc_001",
  doc_name: "SaaS_MSA_v2.pdf",
  agent_path: "manager_worker",
  playbook_id: "playbook_saas_001",
  score: 92,
  status: "completed",
  created_at: "2025-10-06T10:23:45Z",
  completed_at: "2025-10-06T10:26:32Z",
  total_duration_ms: 167000,
  steps: [
    {
      step_id: "step_1",
      step_name: "Manager: Task Decomposition",
      agent: "Manager",
      status: "success",
      input: "Parse contract sections 1-15 for risk assessment",
      output: "Identified 8 clauses requiring review: liability, indemnity, termination, data protection, IP rights, payment terms, warranties, dispute resolution",
      duration_ms: 2340,
      timestamp: "2025-10-06T10:23:47Z",
      metadata: {
        model: "gpt-4",
        tokens_in: 1250,
        tokens_out: 340,
        cost_usd: 0.045,
      },
    },
    {
      step_id: "step_2",
      step_name: "Worker: Clause Parser",
      agent: "ClauseParser",
      status: "success",
      input: "Extract and normalize clause text from sections 1-15",
      output: "Successfully parsed 8 clauses with metadata (section numbers, headings, dependencies)",
      duration_ms: 1890,
      timestamp: "2025-10-06T10:23:49Z",
      metadata: {
        model: "gpt-3.5-turbo",
        tokens_in: 3200,
        tokens_out: 890,
        cost_usd: 0.012,
      },
    },
    {
      step_id: "step_3",
      step_name: "Worker: Policy Retriever",
      agent: "PolicyRetriever",
      status: "success",
      input: "Fetch relevant policies for: liability, indemnity, data protection",
      output: "Retrieved 12 policy rules from playbook_saas_001: liability cap (12 months fees), indemnity exclusions (force majeure), GDPR compliance requirements",
      duration_ms: 450,
      timestamp: "2025-10-06T10:23:50Z",
      metadata: {
        tool: "policy_db_lookup",
        cache_hit: true,
      },
    },
    {
      step_id: "step_4",
      step_name: "Worker: Risk Tagger (Parallel 1/3)",
      agent: "RiskTagger",
      status: "success",
      input: "Assess risk for clauses: liability, indemnity, termination",
      output: "Liability: HIGH (unlimited cap), Indemnity: MEDIUM (broad scope), Termination: LOW (standard 90-day notice)",
      duration_ms: 3120,
      timestamp: "2025-10-06T10:23:53Z",
      metadata: {
        model: "gpt-4",
        tokens_in: 2100,
        tokens_out: 560,
        cost_usd: 0.067,
      },
    },
    {
      step_id: "step_5",
      step_name: "Worker: Risk Tagger (Parallel 2/3)",
      agent: "RiskTagger",
      status: "success",
      input: "Assess risk for clauses: data protection, IP rights, payment",
      output: "Data Protection: MEDIUM (missing DPA reference), IP Rights: LOW (standard assignment), Payment: LOW (Net 30)",
      duration_ms: 2980,
      timestamp: "2025-10-06T10:23:56Z",
      metadata: {
        model: "gpt-4",
        tokens_in: 1950,
        tokens_out: 490,
        cost_usd: 0.061,
      },
    },
    {
      step_id: "step_6",
      step_name: "Worker: Risk Tagger (Parallel 3/3)",
      agent: "RiskTagger",
      status: "success",
      input: "Assess risk for clauses: warranties, dispute resolution",
      output: "Warranties: MEDIUM (disclaimer too broad), Dispute Resolution: LOW (standard arbitration)",
      duration_ms: 2450,
      timestamp: "2025-10-06T10:23:58Z",
      metadata: {
        model: "gpt-4",
        tokens_in: 1680,
        tokens_out: 420,
        cost_usd: 0.053,
      },
    },
    {
      step_id: "step_7",
      step_name: "Worker: Rewriter",
      agent: "Rewriter",
      status: "success",
      input: "Generate redline proposals for HIGH and MEDIUM risk clauses",
      output: "Generated 5 proposals: (1) Liability cap at 12 months fees, (2) Indemnity exclusions for force majeure, (3) Add DPA reference, (4) Narrow warranty disclaimer, (5) Add subprocessor list",
      duration_ms: 4890,
      timestamp: "2025-10-06T10:24:03Z",
      metadata: {
        model: "gpt-4",
        tokens_in: 4200,
        tokens_out: 1340,
        cost_usd: 0.142,
      },
    },
    {
      step_id: "step_8",
      step_name: "Reviewer: Quality Check",
      agent: "Reviewer",
      status: "success",
      input: "Validate proposals against checklist: policy alignment, number consistency, tone, evidence",
      output: "All 5 proposals passed review. Score: 92/100. Minor issues: (1) Liability cap wording could be clearer, (2) DPA reference needs specific article citation",
      duration_ms: 3240,
      timestamp: "2025-10-06T10:24:06Z",
      metadata: {
        model: "gpt-4",
        tokens_in: 2800,
        tokens_out: 680,
        cost_usd: 0.089,
      },
    },
  ],
  summary: {
    total_steps: 8,
    successful_steps: 8,
    failed_steps: 0,
    total_cost_usd: 0.469,
    total_tokens: 12890,
    high_risk_clauses: 1,
    medium_risk_clauses: 3,
    low_risk_clauses: 4,
  },
};

export default function ReplayPage() {
  const [selectedRun, setSelectedRun] = useState<string>("");
  const [traceDetails, setTraceDetails] = useState<any>(null);
  const [editingStep, setEditingStep] = useState<string | null>(null);
  const [modifiedInput, setModifiedInput] = useState<string>("");
  const [replayResult, setReplayResult] = useState<string | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  const handleLoadTrace = (runId: string) => {
    setSelectedRun(runId);
    // In real implementation, this would call: api.getBlackboard(runId)
    setTraceDetails(mockTraceDetails);
    setReplayResult(null);
    setShowComparison(false);
  };

  const handleEditStep = (stepId: string, currentInput: string) => {
    setEditingStep(stepId);
    setModifiedInput(currentInput);
  };

  const handleSaveEdit = () => {
    // In real implementation, update the trace
    setEditingStep(null);
  };

  const handleReplay = () => {
    // In real implementation, this would call: api.replay(selectedRun)
    const newRunId = `run_replay_${Date.now()}`;
    setReplayResult(newRunId);
    setShowComparison(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-blue-600" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Replay & Debug
        </h1>
        <p className="text-gray-600">
          Replay previous runs, modify agent inputs, and compare results
        </p>
      </div>

      {/* Run Selection */}
      <div className="card mb-8">
        <div className="flex items-center mb-6">
          <Search className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900">
            Select Run to Replay
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-3">
          {mockRuns.map((run) => (
            <button
              key={run.run_id}
              onClick={() => handleLoadTrace(run.run_id)}
              className={`flex items-center justify-between p-4 border-2 rounded-lg text-left transition-all ${
                selectedRun === run.run_id
                  ? "border-primary-500 bg-primary-50"
                  : "border-gray-200 hover:border-primary-300 hover:bg-gray-50"
              }`}
            >
              <div className="flex items-center space-x-4 flex-1">
                <div
                  className={`w-2 h-2 rounded-full ${
                    run.status === "completed" ? "bg-green-500" : "bg-red-500"
                  }`}
                ></div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{run.doc_name}</p>
                  <p className="text-xs text-gray-500 font-mono mt-1">
                    {run.run_id}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-6 text-sm">
                <div className="text-center">
                  <p className="text-gray-600 text-xs">Agent</p>
                  <p className="font-medium text-gray-900">
                    {run.agent_path.replace("_", "-")}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-gray-600 text-xs">Score</p>
                  <p className="font-semibold text-gray-900">{run.score}/100</p>
                </div>
                <div className="text-center">
                  <p className="text-gray-600 text-xs">Steps</p>
                  <p className="font-medium text-gray-900">{run.total_steps}</p>
                </div>
                <div className="text-center">
                  <p className="text-gray-600 text-xs">Time</p>
                  <p className="text-gray-700">
                    {new Date(run.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Trace Details */}
      {traceDetails && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Total Steps</p>
                <Zap className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {traceDetails.summary.total_steps}
              </p>
              <p className="text-sm text-green-600 mt-1">
                {traceDetails.summary.successful_steps} successful
              </p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Total Cost</p>
                <FileText className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                ${traceDetails.summary.total_cost_usd.toFixed(3)}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {traceDetails.summary.total_tokens.toLocaleString()} tokens
              </p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Duration</p>
                <Clock className="w-5 h-5 text-orange-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {(traceDetails.total_duration_ms / 1000).toFixed(1)}s
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {(
                  traceDetails.total_duration_ms /
                  traceDetails.summary.total_steps
                ).toFixed(0)}
                ms/step
              </p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Risk Clauses</p>
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div className="flex items-center space-x-2 mt-2">
                <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
                  {traceDetails.summary.high_risk_clauses} High
                </span>
                <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs font-semibold rounded">
                  {traceDetails.summary.medium_risk_clauses} Med
                </span>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
                  {traceDetails.summary.low_risk_clauses} Low
                </span>
              </div>
            </div>
          </div>

          {/* Step-by-Step Trace */}
          <div className="card mb-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <RotateCcw className="w-6 h-6 text-primary-600 mr-3" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Execution Trace
                </h2>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleReplay}
                  className="btn-primary flex items-center"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Replay Run
                </button>
                <button className="btn-secondary flex items-center">
                  <Copy className="w-4 h-4 mr-2" />
                  Clone & Modify
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {traceDetails.steps.map((step: any, index: number) => (
                <div
                  key={step.step_id}
                  className="border border-gray-200 rounded-lg overflow-hidden"
                >
                  {/* Step Header */}
                  <div className="bg-gray-50 px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                        {index + 1}
                      </span>
                      {getStatusIcon(step.status)}
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {step.step_name}
                        </h3>
                        <p className="text-xs text-gray-500">
                          {step.agent} • {step.duration_ms}ms
                          {step.metadata?.model && ` • ${step.metadata.model}`}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleEditStep(step.step_id, step.input)}
                      className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="Edit input"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Step Details */}
                  <div className="p-4 space-y-3">
                    {/* Input */}
                    <div>
                      <label className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                        Input
                      </label>
                      {editingStep === step.step_id ? (
                        <div className="mt-1">
                          <textarea
                            className="input font-mono text-sm"
                            rows={3}
                            value={modifiedInput}
                            onChange={(e) => setModifiedInput(e.target.value)}
                          />
                          <div className="flex space-x-2 mt-2">
                            <button
                              onClick={handleSaveEdit}
                              className="btn-primary text-sm"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => setEditingStep(null)}
                              className="btn-secondary text-sm"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="mt-1 text-sm text-gray-700 bg-gray-50 p-3 rounded border border-gray-200">
                          {step.input}
                        </p>
                      )}
                    </div>

                    {/* Output */}
                    <div>
                      <label className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                        Output
                      </label>
                      <p className="mt-1 text-sm text-gray-700 bg-green-50 p-3 rounded border border-green-200">
                        {step.output}
                      </p>
                    </div>

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-4 pt-2 border-t border-gray-200">
                      {step.metadata?.tokens_in && (
                        <div className="text-xs">
                          <span className="text-gray-600">Tokens In:</span>
                          <span className="font-semibold text-gray-900 ml-1">
                            {step.metadata.tokens_in.toLocaleString()}
                          </span>
                        </div>
                      )}
                      {step.metadata?.tokens_out && (
                        <div className="text-xs">
                          <span className="text-gray-600">Tokens Out:</span>
                          <span className="font-semibold text-gray-900 ml-1">
                            {step.metadata.tokens_out.toLocaleString()}
                          </span>
                        </div>
                      )}
                      {step.metadata?.cost_usd && (
                        <div className="text-xs">
                          <span className="text-gray-600">Cost:</span>
                          <span className="font-semibold text-green-700 ml-1">
                            ${step.metadata.cost_usd.toFixed(3)}
                          </span>
                        </div>
                      )}
                      {step.metadata?.cache_hit && (
                        <div className="text-xs">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded font-semibold">
                            Cache Hit
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Replay Result */}
          {replayResult && (
            <div className="card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200">
              <div className="flex items-center mb-4">
                <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Replay Complete!
                </h3>
              </div>
              <p className="text-gray-700 mb-4">
                New run created with ID:{" "}
                <code className="bg-white px-2 py-1 rounded font-mono text-sm">
                  {replayResult}
                </code>
              </p>
              <div className="flex space-x-3">
                <Link
                  href={`/run/${replayResult}`}
                  className="btn-primary flex items-center"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  View New Run
                </Link>
                <button
                  onClick={() => setShowComparison(!showComparison)}
                  className="btn-secondary flex items-center"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  {showComparison ? "Hide" : "Show"} Comparison
                </button>
              </div>

              {/* Comparison View */}
              {showComparison && (
                <div className="mt-6 pt-6 border-t border-green-300">
                  <h4 className="font-semibold text-gray-900 mb-3">
                    Comparison: Original vs Replay
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Original Run
                      </p>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Score:</span>
                          <span className="font-semibold">92/100</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Duration:</span>
                          <span className="font-semibold">167s</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Cost:</span>
                          <span className="font-semibold">$0.469</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">High Risk:</span>
                          <span className="font-semibold">1</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Replay Run
                      </p>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Score:</span>
                          <span className="font-semibold text-green-600">
                            94/100 (+2)
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Duration:</span>
                          <span className="font-semibold text-green-600">
                            152s (-15s)
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Cost:</span>
                          <span className="font-semibold text-green-600">
                            $0.423 (-$0.046)
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">High Risk:</span>
                          <span className="font-semibold text-green-600">
                            0 (-1)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* What-If Scenarios */}
          <div className="card bg-blue-50 border-2 border-blue-200">
            <div className="flex items-center mb-4">
              <Settings className="w-6 h-6 text-blue-600 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900">
                What-If Scenarios
              </h3>
            </div>
            <p className="text-sm text-gray-700 mb-4">
              Modify agent inputs, change tools, or adjust prompts to see how
              different decisions affect the outcome.
            </p>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>
                  Edit any step's input and replay from that point forward
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>
                  Switch between agent paths (Manager–Worker ↔ Planner–Executor)
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Compare results side-by-side with original run</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>
                  Track cost and quality improvements across iterations
                </span>
              </li>
            </ul>
          </div>
        </>
      )}

      {/* Empty State */}
      {!traceDetails && (
        <div className="card text-center py-12">
          <RotateCcw className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2">No trace selected</p>
          <p className="text-sm text-gray-500">
            Select a run from the list above to view and replay its execution
            trace
          </p>
        </div>
      )}
    </div>
  );
}
