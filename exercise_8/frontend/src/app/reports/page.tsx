"use client";

import { useState } from "react";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Clock,
  DollarSign,
  CheckCircle,
  AlertTriangle,
  Users,
  FileText,
  Activity,
  Zap,
} from "lucide-react";

// Mock data for demonstration
const mockData = {
  summary: {
    totalRuns: 147,
    totalDocuments: 89,
    avgScore: 87.3,
    totalCost: 342.56,
    successRate: 94.2,
    avgLatency: 2847,
  },
  performance: {
    p50_latency_ms: 2340,
    p95_latency_ms: 4820,
    p99_latency_ms: 6150,
    avg_latency_ms: 2847,
    min_latency_ms: 1240,
    max_latency_ms: 8930,
  },
  quality: {
    reviewer_pass_rate: 0.942,
    policy_match_precision: 0.891,
    high_risk_mitigation_rate: 0.876,
    avg_clauses_per_doc: 23.4,
    avg_rework_loops: 1.3,
  },
  cost: {
    total_usd: 342.56,
    avg_per_document: 3.85,
    avg_per_run: 2.33,
    by_agent_path: {
      manager_worker: 128.45,
      planner_executor: 142.78,
      reviewer_referee: 71.33,
    },
    trend_7d: -12.3, // percentage change
  },
  recentRuns: [
    {
      run_id: "run_abc123",
      doc_name: "SaaS_MSA_v2.pdf",
      agent_path: "manager_worker",
      score: 92,
      latency_ms: 2340,
      cost_usd: 3.45,
      status: "completed",
      timestamp: "2025-10-06T10:23:45Z",
    },
    {
      run_id: "run_def456",
      doc_name: "NDA_Template.docx",
      agent_path: "planner_executor",
      score: 88,
      latency_ms: 3120,
      cost_usd: 4.12,
      status: "completed",
      timestamp: "2025-10-06T09:15:22Z",
    },
    {
      run_id: "run_ghi789",
      doc_name: "DPA_GDPR.pdf",
      agent_path: "reviewer_referee",
      score: 85,
      latency_ms: 4820,
      cost_usd: 5.67,
      status: "completed",
      timestamp: "2025-10-06T08:42:11Z",
    },
    {
      run_id: "run_jkl012",
      doc_name: "Service_Agreement.pdf",
      agent_path: "manager_worker",
      score: 90,
      latency_ms: 2890,
      cost_usd: 3.89,
      status: "completed",
      timestamp: "2025-10-06T07:33:56Z",
    },
    {
      run_id: "run_mno345",
      doc_name: "Partnership_Contract.docx",
      agent_path: "planner_executor",
      score: 78,
      latency_ms: 5230,
      cost_usd: 6.23,
      status: "failed",
      timestamp: "2025-10-06T06:18:34Z",
    },
  ],
  agentPathStats: [
    {
      name: "Manager–Worker",
      runs: 56,
      avg_score: 89.2,
      avg_latency: 2456,
      success_rate: 96.4,
      cost: 128.45,
    },
    {
      name: "Planner–Executor",
      runs: 62,
      avg_score: 86.7,
      avg_latency: 3124,
      success_rate: 93.5,
      cost: 142.78,
    },
    {
      name: "Reviewer/Referee",
      runs: 29,
      avg_score: 85.1,
      avg_latency: 3890,
      success_rate: 91.2,
      cost: 71.33,
    },
  ],
};

export default function ReportsPage() {
  const [timeRange, setTimeRange] = useState("7d");

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatLatency = (ms: number) => {
    return `${ms.toLocaleString()}ms`;
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Reports & Analytics
          </h1>
          <p className="text-gray-600">
            Performance metrics, quality indicators, and cost analysis
          </p>
        </div>
        <div className="flex space-x-2">
          {["24h", "7d", "30d", "90d"].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                timeRange === range
                  ? "bg-primary-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Runs</p>
            <Activity className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {mockData.summary.totalRuns}
          </p>
          <p className="text-sm text-green-600 mt-1 flex items-center">
            <TrendingUp className="w-4 h-4 mr-1" />
            +12.5% from last period
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Success Rate</p>
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {mockData.summary.successRate}%
          </p>
          <p className="text-sm text-green-600 mt-1 flex items-center">
            <TrendingUp className="w-4 h-4 mr-1" />
            +2.3% from last period
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Avg Score</p>
            <BarChart3 className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {mockData.summary.avgScore}/100
          </p>
          <p className="text-sm text-green-600 mt-1 flex items-center">
            <TrendingUp className="w-4 h-4 mr-1" />
            +4.2 from last period
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Avg Latency (P50)</p>
            <Clock className="w-5 h-5 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {formatLatency(mockData.performance.p50_latency_ms)}
          </p>
          <p className="text-sm text-green-600 mt-1 flex items-center">
            <TrendingDown className="w-4 h-4 mr-1" />
            -8.4% faster
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Cost</p>
            <DollarSign className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(mockData.cost.total_usd)}
          </p>
          <p className="text-sm text-green-600 mt-1 flex items-center">
            <TrendingDown className="w-4 h-4 mr-1" />
            {Math.abs(mockData.cost.trend_7d)}% lower
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Documents Processed</p>
            <FileText className="w-5 h-5 text-indigo-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {mockData.summary.totalDocuments}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            Avg {formatCurrency(mockData.cost.avg_per_document)}/doc
          </p>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center mb-6">
            <Zap className="w-6 h-6 text-yellow-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Latency Distribution
            </h2>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">P50 (Median)</span>
                <span className="font-semibold text-gray-900">
                  {formatLatency(mockData.performance.p50_latency_ms)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: "45%" }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">P95</span>
                <span className="font-semibold text-gray-900">
                  {formatLatency(mockData.performance.p95_latency_ms)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-500 h-2 rounded-full"
                  style={{ width: "75%" }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">P99</span>
                <span className="font-semibold text-gray-900">
                  {formatLatency(mockData.performance.p99_latency_ms)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: "95%" }}
                ></div>
              </div>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Min</p>
                  <p className="font-semibold text-gray-900">
                    {formatLatency(mockData.performance.min_latency_ms)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Max</p>
                  <p className="font-semibold text-gray-900">
                    {formatLatency(mockData.performance.max_latency_ms)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center mb-6">
            <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Quality Metrics
            </h2>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Reviewer Pass Rate</span>
                <span className="font-semibold text-gray-900">
                  {formatPercent(mockData.quality.reviewer_pass_rate)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{
                    width: `${mockData.quality.reviewer_pass_rate * 100}%`,
                  }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Policy Match Precision</span>
                <span className="font-semibold text-gray-900">
                  {formatPercent(mockData.quality.policy_match_precision)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{
                    width: `${mockData.quality.policy_match_precision * 100}%`,
                  }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">High Risk Mitigation</span>
                <span className="font-semibold text-gray-900">
                  {formatPercent(mockData.quality.high_risk_mitigation_rate)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{
                    width: `${
                      mockData.quality.high_risk_mitigation_rate * 100
                    }%`,
                  }}
                ></div>
              </div>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Avg Clauses/Doc</p>
                  <p className="font-semibold text-gray-900">
                    {mockData.quality.avg_clauses_per_doc}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Avg Rework Loops</p>
                  <p className="font-semibold text-gray-900">
                    {mockData.quality.avg_rework_loops}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Path Comparison */}
      <div className="card mb-8">
        <div className="flex items-center mb-6">
          <Users className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900">
            Agent Path Performance
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Agent Path
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Runs
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Avg Score
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Avg Latency
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Success Rate
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Total Cost
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {mockData.agentPathStats.map((stat, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {stat.name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {stat.runs}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {stat.avg_score}/100
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {formatLatency(stat.avg_latency)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        stat.success_rate >= 95
                          ? "bg-green-100 text-green-800"
                          : stat.success_rate >= 90
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {stat.success_rate}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm font-semibold text-gray-900">
                    {formatCurrency(stat.cost)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Runs */}
      <div className="card">
        <div className="flex items-center mb-6">
          <Activity className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900">Recent Runs</h2>
        </div>
        <div className="space-y-3">
          {mockData.recentRuns.map((run) => (
            <div
              key={run.run_id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center space-x-4 flex-1">
                <div
                  className={`w-2 h-2 rounded-full ${
                    run.status === "completed" ? "bg-green-500" : "bg-red-500"
                  }`}
                ></div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {run.doc_name}
                  </p>
                  <p className="text-xs text-gray-500 font-mono">
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
                  <p className="text-gray-600 text-xs">Latency</p>
                  <p className="font-medium text-gray-900">
                    {formatLatency(run.latency_ms)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-gray-600 text-xs">Cost</p>
                  <p className="font-semibold text-gray-900">
                    {formatCurrency(run.cost_usd)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-gray-600 text-xs">Time</p>
                  <p className="text-gray-700">
                    {new Date(run.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SLO Summary */}
      <div className="mt-8 card bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200">
        <div className="flex items-center mb-4">
          <AlertTriangle className="w-6 h-6 text-primary-600 mr-3" />
          <h3 className="text-lg font-semibold text-gray-900">SLO Status</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Latency SLO (P95)</p>
            <p className="text-2xl font-bold text-green-600">✓ Met</p>
            <p className="text-xs text-gray-500 mt-1">
              Target: &lt;5000ms | Actual: 4820ms
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Quality SLO</p>
            <p className="text-2xl font-bold text-green-600">✓ Met</p>
            <p className="text-xs text-gray-500 mt-1">
              Target: &gt;90% | Actual: 94.2%
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Cost SLO</p>
            <p className="text-2xl font-bold text-green-600">✓ Met</p>
            <p className="text-xs text-gray-500 mt-1">
              Target: &lt;$5/doc | Actual: $3.85/doc
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
