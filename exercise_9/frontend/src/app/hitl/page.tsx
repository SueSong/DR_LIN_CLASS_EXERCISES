"use client";

import { useState, useEffect } from "react";
import { getHITLQueue, getHITLDetails, respondToHITL } from "@/lib/api";

export default function HITLPage() {
  const [queue, setQueue] = useState<any[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [decisions, setDecisions] = useState<Record<string, any>>({});
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadQueue = async () => {
    try {
      const items = await getHITLQueue();
      setQueue(items);
    } catch (error) {
      console.error("Failed to load HITL queue:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectItem = async (hitlId: string) => {
    try {
      const details = await getHITLDetails(hitlId);
      setSelectedItem(details);
      
      // Initialize decisions
      const initialDecisions: Record<string, any> = {};
      details.items.forEach((item: any) => {
        initialDecisions[item.id] = {
          item_id: item.id,
          decision: "approve",
          comments: "",
          modified_content: null
        };
      });
      setDecisions(initialDecisions);
    } catch (error) {
      console.error("Failed to load HITL details:", error);
    }
  };

  const handleDecisionChange = (itemId: string, field: string, value: any) => {
    setDecisions(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));
  };

  const handleSubmit = async () => {
    if (!selectedItem) return;

    setSubmitting(true);
    try {
      const decisionList = Object.values(decisions);
      await respondToHITL(selectedItem.hitl_id, decisionList);
      alert("Decisions submitted successfully!");
      setSelectedItem(null);
      setDecisions({});
      await loadQueue();
    } catch (error) {
      console.error("Failed to submit decisions:", error);
      alert("Failed to submit decisions");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        Human-in-the-Loop (HITL) Queue
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Queue List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              Pending Approvals
            </h2>
            
            {loading ? (
              <p className="text-gray-600">Loading queue...</p>
            ) : queue.length === 0 ? (
              <p className="text-gray-600">No pending approvals.</p>
            ) : (
              <div className="space-y-3">
                {queue.map((item) => (
                  <div
                    key={item.hitl_id}
                    onClick={() => handleSelectItem(item.hitl_id)}
                    className={`border rounded-lg p-3 cursor-pointer hover:bg-gray-50 ${
                      selectedItem?.hitl_id === item.hitl_id ? "border-blue-500 bg-blue-50" : "border-gray-200"
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-sm text-gray-800">
                        {item.stage}
                      </span>
                      <span className="text-xs text-yellow-600 bg-yellow-100 px-2 py-1 rounded">
                        {item.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">
                      Items: {item.item_count}
                    </p>
                    <p className="text-xs text-gray-500">
                      Created: {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Review Panel */}
        <div className="lg:col-span-2">
          {selectedItem ? (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-800">
                      Review: {selectedItem.stage}
                    </h2>
                    <p className="text-sm text-gray-600">
                      Run ID: <span className="font-mono text-xs">{selectedItem.run_id}</span>
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedItem(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>

                <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-800 mb-2">
                    Approval Required
                  </h3>
                  <p className="text-sm text-blue-700">
                    Please review each item below and provide your decision. 
                    You can approve, reject, or modify the proposed actions.
                  </p>
                </div>

                <div className="space-y-4">
                  {selectedItem.items.map((item: any, idx: number) => (
                    <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="font-medium text-gray-800">
                          Item {idx + 1}: {item.type || item.pii_type || item.heading}
                        </h4>
                        {item.risk_level && (
                          <span className={`text-xs px-2 py-1 rounded ${
                            item.risk_level === "high" ? "bg-red-100 text-red-800" :
                            item.risk_level === "medium" ? "bg-yellow-100 text-yellow-800" :
                            "bg-green-100 text-green-800"
                          }`}>
                            {item.risk_level} risk
                          </span>
                        )}
                      </div>

                      {/* Item Details */}
                      <div className="bg-gray-50 rounded p-3 mb-3 text-sm">
                        {item.text && (
                          <p className="mb-2"><strong>Original:</strong> {item.text}</p>
                        )}
                        {item.redacted_value && (
                          <p className="mb-2"><strong>Redacted:</strong> {item.redacted_value}</p>
                        )}
                        {item.context && (
                          <p className="mb-2 text-xs text-gray-600">
                            <strong>Context:</strong> ...{item.context}...
                          </p>
                        )}
                        {item.rationale && (
                          <p className="text-xs text-gray-600">
                            <strong>Rationale:</strong> {item.rationale}
                          </p>
                        )}
                      </div>

                      {/* Decision Controls */}
                      <div className="space-y-2">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Decision
                          </label>
                          <select
                            value={decisions[item.id]?.decision || "approve"}
                            onChange={(e) => handleDecisionChange(item.id, "decision", e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="approve">✓ Approve</option>
                            <option value="reject">✗ Reject</option>
                            <option value="modify">✎ Modify</option>
                          </select>
                        </div>

                        {decisions[item.id]?.decision === "modify" && (
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Modified Content
                            </label>
                            <input
                              type="text"
                              value={decisions[item.id]?.modified_content || ""}
                              onChange={(e) => handleDecisionChange(item.id, "modified_content", e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Enter modified value..."
                            />
                          </div>
                        )}

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Comments (optional)
                          </label>
                          <textarea
                            value={decisions[item.id]?.comments || ""}
                            onChange={(e) => handleDecisionChange(item.id, "comments", e.target.value)}
                            rows={2}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Add any notes or justification..."
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    onClick={() => setSelectedItem(null)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {submitting ? "Submitting..." : "Submit All Decisions"}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-600">
              <p>Select an item from the queue to review.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

