"use client";

import { useState, useEffect } from "react";
import { getAuditLogs } from "@/lib/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const auditLogs = await getAuditLogs(200);
      setLogs(auditLogs);
    } catch (error) {
      console.error("Failed to load audit logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter !== "all" && log.action !== filter) return false;
    if (searchTerm && !JSON.stringify(log).toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const actionTypes = Array.from(new Set(logs.map(log => log.action))).sort();

  const getActionColor = (action: string) => {
    if (action.includes("upload") || action.includes("created")) return "text-green-600 bg-green-50";
    if (action.includes("hitl")) return "text-yellow-600 bg-yellow-50";
    if (action.includes("redteam")) return "text-red-600 bg-red-50";
    if (action.includes("fail")) return "text-red-600 bg-red-50";
    return "text-blue-600 bg-blue-50";
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        📋 Audit Trail & Compliance Logs
      </h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h2 className="font-semibold text-blue-800 mb-2">
          Complete Audit Trail
        </h2>
        <p className="text-sm text-blue-700">
          All actions are logged for compliance and security monitoring. 
          Logs include document uploads, review runs, HITL decisions, and red team tests.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Action
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Actions</option>
              {actionTypes.map((action) => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Logs
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by any field..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Showing {filteredLogs.length} of {logs.length} logs</span>
          <button
            onClick={loadLogs}
            className="text-blue-600 hover:underline"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {loading ? (
          <div className="p-6 text-center text-gray-600">
            Loading audit logs...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-6 text-center text-gray-600">
            No audit logs found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {log.user || "system"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <details className="cursor-pointer">
                        <summary className="hover:text-blue-600">
                          View Details
                        </summary>
                        <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(log, null, 2)}
                        </pre>
                      </details>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Total Events
          </h3>
          <p className="text-3xl font-bold text-blue-600">{logs.length}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            HITL Actions
          </h3>
          <p className="text-3xl font-bold text-yellow-600">
            {logs.filter(l => l.action.includes("hitl")).length}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Red Team Tests
          </h3>
          <p className="text-3xl font-bold text-red-600">
            {logs.filter(l => l.action.includes("redteam")).length}
          </p>
        </div>
      </div>
    </div>
  );
}

