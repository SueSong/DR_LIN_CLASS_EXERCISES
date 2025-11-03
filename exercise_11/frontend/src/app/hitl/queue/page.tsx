"use client";

import { useState, useEffect } from "react";

interface HITLItem {
  hitl_id: string;
  session_id: string;
  parent_name: string;
  message: string;
  classification: string;
  primary_category?: string;
  detected_pii: Array<{
    type: string;
    text: string;
    context: string;
  }>;
  status: string;
  created_at: string;
  mentor_reply?: string;
  mentor_replied_at?: string;
}

export default function HITLQueuePage() {
  const [queue, setQueue] = useState<HITLItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<HITLItem | null>(null);
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadQueue();
    // Poll every 30 seconds for new items (reduced from 5s to save resources)
    const interval = setInterval(loadQueue, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadQueue = async () => {
    try {
      const response = await fetch("http://localhost:8011/api/hitl/queue?status=pending");
      if (response.ok) {
        const data = await response.json();
        setQueue(data.items || []);
      }
    } catch (error) {
      console.error("Failed to load HITL queue:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadItemDetails = async (hitlId: string) => {
    try {
      const response = await fetch(`http://localhost:8011/api/hitl/${hitlId}`);
      if (response.ok) {
        const item = await response.json();
        setSelectedItem(item);
        setReply(item.mentor_reply || "");
      }
    } catch (error) {
      console.error("Failed to load HITL item:", error);
    }
  };

  const submitReply = async () => {
    if (!selectedItem || !reply.trim()) {
      alert("Please enter a mentor reply");
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(
        `http://localhost:8011/api/hitl/${selectedItem.hitl_id}/reply`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mentor_reply: reply.trim(),
          }),
        }
      );

      if (response.ok) {
        alert("Reply submitted successfully! The parent will see this in their chat.");
        setSelectedItem(null);
        setReply("");
        loadQueue(); // Refresh queue
      } else {
        const error = await response.json();
        alert(`Failed to submit reply: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Failed to submit reply:", error);
      alert("Failed to submit reply. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getClassificationColor = (classification: string) => {
    switch (classification.toLowerCase()) {
      case "escalate":
        return "bg-red-100 text-red-800 border-red-300";
      case "blocked":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Human-in-the-Loop Queue
          </h1>
          <p className="text-slate-600 mb-8">
            Review crisis situations and provide mentor guidance
          </p>

          {loading && queue.length === 0 ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-slate-600">Loading queue...</p>
            </div>
          ) : queue.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-600 text-lg">
                ✨ No pending items in the queue. All clear!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Queue List */}
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold text-slate-900">
                  Pending Items ({queue.length})
                </h2>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {queue.map((item) => (
                    <div
                      key={item.hitl_id}
                      onClick={() => loadItemDetails(item.hitl_id)}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        selectedItem?.hitl_id === item.hitl_id
                          ? "border-blue-500 bg-blue-50"
                          : "border-slate-200 bg-white hover:border-blue-300 hover:bg-blue-50/50"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="font-semibold text-slate-900">
                            {item.parent_name}
                          </p>
                          <p className="text-sm text-slate-500">
                            Session: {item.session_id}
                          </p>
                        </div>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium border ${getClassificationColor(
                            item.classification
                          )}`}
                        >
                          {item.classification.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-slate-700 text-sm line-clamp-2 mb-2">
                        {item.message}
                      </p>
                      {item.primary_category && (
                        <p className="text-xs text-slate-500">
                          Category: {item.primary_category}
                        </p>
                      )}
                      {item.detected_pii && item.detected_pii.length > 0 && (
                        <p className="text-xs text-orange-600 mt-1">
                          ⚠️ {item.detected_pii.length} PII detected
                        </p>
                      )}
                      <p className="text-xs text-slate-400 mt-2">
                        {formatDate(item.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Details and Reply */}
              <div className="space-y-4">
                {selectedItem ? (
                  <>
                    <h2 className="text-2xl font-semibold text-slate-900">
                      Review & Reply
                    </h2>
                    <div className="bg-slate-50 rounded-xl p-6 space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Original Message
                        </label>
                        <div className="bg-white p-4 rounded-lg border border-slate-200">
                          <p className="text-slate-900">{selectedItem.message}</p>
                        </div>
                      </div>

                      {selectedItem.primary_category && (
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">
                            Category
                          </label>
                          <p className="text-slate-900">{selectedItem.primary_category}</p>
                        </div>
                      )}

                      {selectedItem.detected_pii &&
                        selectedItem.detected_pii.length > 0 && (
                          <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">
                              Detected PII ({selectedItem.detected_pii.length})
                            </label>
                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 space-y-2">
                              {selectedItem.detected_pii.map((pii, idx) => (
                                <div key={idx} className="text-sm">
                                  <span className="font-medium text-yellow-800">
                                    {pii.type}:
                                  </span>{" "}
                                  <span className="text-yellow-700">{pii.text}</span>
                                  {pii.context && (
                                    <p className="text-xs text-yellow-600 mt-1">
                                      Context: ...{pii.context}...
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Session Info
                        </label>
                        <div className="text-sm text-slate-600 space-y-1">
                          <p>Session ID: {selectedItem.session_id}</p>
                          <p>Parent: {selectedItem.parent_name}</p>
                          <p>Received: {formatDate(selectedItem.created_at)}</p>
                        </div>
                      </div>

                      <div>
                        <label
                          htmlFor="mentor_reply"
                          className="block text-sm font-medium text-slate-700 mb-2"
                        >
                          Your Reply (will be sent to parent)
                        </label>
                        <textarea
                          id="mentor_reply"
                          value={reply}
                          onChange={(e) => setReply(e.target.value)}
                          placeholder="Enter your guidance and support message for the parent..."
                          className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                          rows={6}
                        />
                      </div>

                      <button
                        onClick={submitReply}
                        disabled={!reply.trim() || submitting}
                        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-slate-400 disabled:cursor-not-allowed transition-colors"
                      >
                        {submitting ? "Submitting..." : "Submit Reply to Parent"}
                      </button>

                      {selectedItem.mentor_reply && (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <p className="text-sm font-medium text-green-800 mb-1">
                            ✓ Reply already sent
                          </p>
                          <p className="text-sm text-green-700">
                            {selectedItem.mentor_reply}
                          </p>
                          <p className="text-xs text-green-600 mt-2">
                            Sent: {formatDate(selectedItem.mentor_replied_at || "")}
                          </p>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="bg-slate-50 rounded-xl p-8 text-center">
                    <p className="text-slate-600">
                      Select an item from the queue to review and reply
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

