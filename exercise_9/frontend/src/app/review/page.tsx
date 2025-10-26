"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { listDocuments, listPolicies, startReviewRun, getRun } from "@/lib/api";

export default function ReviewPage() {
  const searchParams = useSearchParams();
  const docIdParam = searchParams.get("doc_id");

  const [documents, setDocuments] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any[]>([]);
  const [selectedDocId, setSelectedDocId] = useState(docIdParam || "");
  const [selectedPolicyIds, setSelectedPolicyIds] = useState<string[]>([]);
  const [runResult, setRunResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
    loadPolicies();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        setSelectedDocId(docs[0].doc_id);
      }
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  };

  const loadPolicies = async () => {
    try {
      const pols = await listPolicies();
      setPolicies(pols);
      setSelectedPolicyIds(pols.map((p: any) => p.policy_id));
    } catch (error) {
      console.error("Failed to load policies:", error);
    }
  };

  const handleStartReview = async () => {
    if (!selectedDocId) {
      alert("Please select a document");
      return;
    }

    setLoading(true);
    setRunResult(null);

    try {
      const result = await startReviewRun(
        selectedDocId,
        selectedPolicyIds.length > 0 ? selectedPolicyIds : undefined
      );
      
      // Poll for results
      setTimeout(async () => {
        try {
          const run = await getRun(result.run_id);
          setRunResult(run);
        } catch (error) {
          console.error("Failed to get run results:", error);
        }
      }, 2000);
    } catch (error) {
      console.error("Failed to start review:", error);
      alert("Failed to start review");
    } finally {
      setLoading(false);
    }
  };

  const togglePolicy = (policyId: string) => {
    setSelectedPolicyIds((prev) =>
      prev.includes(policyId)
        ? prev.filter((id) => id !== policyId)
        : [...prev, policyId]
    );
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case "high":
        return "text-red-600 bg-red-50";
      case "medium":
        return "text-yellow-600 bg-yellow-50";
      case "low":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Document Review</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              Select Document
            </h2>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select Document --</option>
              {documents.map((doc) => (
                <option key={doc.doc_id} value={doc.doc_id}>
                  {doc.name}
                </option>
              ))}
            </select>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              Select Policies
            </h2>
            <div className="space-y-2">
              {policies.map((policy) => (
                <label
                  key={policy.policy_id}
                  className="flex items-start space-x-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedPolicyIds.includes(policy.policy_id)}
                    onChange={() => togglePolicy(policy.policy_id)}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium text-gray-800">
                      {policy.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {policy.policy_id}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={handleStartReview}
            disabled={loading || !selectedDocId}
            className="w-full bg-green-600 text-white px-4 py-3 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {loading ? "Processing..." : "Start Multi-Agent Review"}
          </button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          {loading && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Running multi-agent pipeline...</p>
                <p className="text-sm text-gray-500 mt-2">
                  Classifier → Extractor → Reviewer → Drafter
                </p>
              </div>
            </div>
          )}

          {runResult && (
            <div className="space-y-6">
              {/* Run Overview */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">
                  Review Results
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Run ID:</span>
                    <p className="font-mono text-xs">{runResult.run_id}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Status:</span>
                    <p className={`font-medium ${
                      runResult.status === "completed" ? "text-green-600" :
                      runResult.status === "awaiting_hitl" ? "text-yellow-600" :
                      runResult.status === "failed" ? "text-red-600" :
                      "text-blue-600"
                    }`}>
                      {runResult.status}
                    </p>
                  </div>
                </div>
                {runResult.hitl_required && (
                  <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800 font-medium">
                      ⚠️ Human-in-the-Loop Review Required
                    </p>
                    <a
                      href="/hitl"
                      className="text-blue-600 hover:underline text-sm"
                    >
                      Go to HITL Queue →
                    </a>
                  </div>
                )}
              </div>

              {/* Agent Results */}
              {Object.entries(runResult.stages || {}).map(([agentName, stage]: [string, any]) => (
                <div key={agentName} className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-3 text-gray-800 capitalize">
                    {agentName} Agent
                  </h3>
                  <div className="mb-2">
                    <span className={`inline-block px-2 py-1 rounded text-sm font-medium ${
                      stage.status === "completed" ? "bg-green-100 text-green-800" :
                      stage.status === "pending" ? "bg-gray-100 text-gray-800" :
                      "bg-blue-100 text-blue-800"
                    }`}>
                      {stage.status}
                    </span>
                  </div>
                  
                  {stage.result && (
                    <div className="mt-4 space-y-3">
                      {/* Classification Results */}
                      {agentName === "classifier" && (
                        <div className="bg-gray-50 rounded p-3 text-sm">
                          <p><strong>Document Type:</strong> {stage.result.doc_type}</p>
                          <p><strong>Sensitivity:</strong> 
                            <span className={`ml-2 px-2 py-1 rounded ${getRiskColor(stage.result.sensitivity_level)}`}>
                              {stage.result.sensitivity_level}
                            </span>
                          </p>
                          {stage.result.risk_factors && stage.result.risk_factors.length > 0 && (
                            <p><strong>Risk Factors:</strong> {stage.result.risk_factors.join(", ")}</p>
                          )}
                        </div>
                      )}

                      {/* Extraction Results */}
                      {agentName === "extractor" && (
                        <div className="space-y-2">
                          <div className="bg-gray-50 rounded p-3 text-sm">
                            <p><strong>Clauses Found:</strong> {stage.result.clauses?.length || 0}</p>
                            <p><strong>PII Entities:</strong> {stage.result.pii_entities?.length || 0}</p>
                            {stage.result.extraction_stats && (
                              <p className="text-red-600">
                                <strong>High-Risk PII:</strong> {stage.result.extraction_stats.high_risk_pii}
                              </p>
                            )}
                          </div>
                          {stage.result.pii_entities && stage.result.pii_entities.length > 0 && (
                            <details className="bg-yellow-50 rounded p-3">
                              <summary className="cursor-pointer font-medium text-sm">
                                View PII Details
                              </summary>
                              <div className="mt-2 space-y-2">
                                {stage.result.pii_entities.slice(0, 5).map((pii: any, idx: number) => (
                                  <div key={idx} className="text-xs border-t pt-2">
                                    <p><strong>Type:</strong> {pii.type}</p>
                                    <p><strong>Risk:</strong> <span className={getRiskColor(pii.risk_level)}>{pii.risk_level}</span></p>
                                    <p><strong>Redacted:</strong> {pii.redacted_value}</p>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                      )}

                      {/* Review Results */}
                      {agentName === "reviewer" && (
                        <div className="space-y-2">
                          <div className={`rounded p-3 ${getRiskColor(stage.result.overall_risk)}`}>
                            <p className="font-medium">
                              Overall Risk: {stage.result.overall_risk?.toUpperCase()}
                            </p>
                          </div>
                          {stage.result.review_summary && (
                            <div className="bg-gray-50 rounded p-3 text-sm">
                              <p><strong>High-Risk Clauses:</strong> {stage.result.review_summary.high_risk_clauses}</p>
                              <p><strong>Policy Violations:</strong> {stage.result.review_summary.policy_violations_count}</p>
                            </div>
                          )}
                          {stage.result.recommendations && stage.result.recommendations.length > 0 && (
                            <details className="bg-blue-50 rounded p-3">
                              <summary className="cursor-pointer font-medium text-sm">
                                Recommendations ({stage.result.recommendations.length})
                              </summary>
                              <ul className="mt-2 space-y-1 text-xs list-disc list-inside">
                                {stage.result.recommendations.map((rec: any, idx: number) => (
                                  <li key={idx}>{rec.description}</li>
                                ))}
                              </ul>
                            </details>
                          )}
                        </div>
                      )}

                      {/* Draft Results */}
                      {agentName === "drafter" && (
                        <div className="space-y-2">
                          <div className="bg-gray-50 rounded p-3 text-sm">
                            <p><strong>Redactions:</strong> {stage.result.redactions_count}</p>
                            <p><strong>Edits:</strong> {stage.result.edits_count}</p>
                            <p><strong>Total Changes:</strong> {stage.result.changes_count}</p>
                          </div>
                          {stage.result.redline_document && (
                            <a
                              href={`/export/${runResult.run_id}/redline`}
                              className="inline-block bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
                            >
                              View Redline Document →
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {!loading && !runResult && (
            <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-600">
              <p>Select a document and click "Start Multi-Agent Review" to begin.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

