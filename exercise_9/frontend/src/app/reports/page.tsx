"use client";

import { useState, useEffect } from "react";
import { getKPIs } from "@/lib/api";

export default function ReportsPage() {
  const [kpis, setKpis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadKPIs();
    const interval = setInterval(loadKPIs, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadKPIs = async () => {
    try {
      const data = await getKPIs();
      setKpis(data);
    } catch (error) {
      console.error("Failed to load KPIs:", error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return "text-green-600";
    if (score >= 0.7) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 0.9) return "bg-green-50 border-green-200";
    if (score >= 0.7) return "bg-yellow-50 border-yellow-200";
    return "bg-red-50 border-red-200";
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading KPIs...</p>
        </div>
      </div>
    );
  }

  if (!kpis) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-center text-gray-600">Failed to load KPI data.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        📊 Key Performance Indicators & Metrics
      </h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h2 className="font-semibold text-blue-800 mb-2">
          System Performance Dashboard
        </h2>
        <p className="text-sm text-blue-700">
          Monitor critical KPIs including accuracy metrics, security performance, 
          and operational efficiency. Real-time updates every 10 seconds.
        </p>
      </div>

      {/* Primary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className={`rounded-lg shadow-md p-6 border ${getScoreBg(kpis.clause_extraction_accuracy)}`}>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Clause Extraction Accuracy
          </h3>
          <p className={`text-4xl font-bold ${getScoreColor(kpis.clause_extraction_accuracy)}`}>
            {(kpis.clause_extraction_accuracy * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Target: ≥90%
          </p>
        </div>

        <div className={`rounded-lg shadow-md p-6 border ${getScoreBg(kpis.pii_f1_score)}`}>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            PII F1 Score
          </h3>
          <p className={`text-4xl font-bold ${getScoreColor(kpis.pii_f1_score)}`}>
            {(kpis.pii_f1_score * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Precision & Recall Balance
          </p>
        </div>

        <div className={`rounded-lg shadow-md p-6 border ${
          kpis.unauthorized_disclosures === 0 ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
        }`}>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Unauthorized Disclosures
          </h3>
          <p className={`text-4xl font-bold ${
            kpis.unauthorized_disclosures === 0 ? "text-green-600" : "text-red-600"
          }`}>
            {kpis.unauthorized_disclosures}
          </p>
          <p className="text-xs text-gray-600 mt-2">
            🎯 Target: ZERO
          </p>
        </div>

        <div className={`rounded-lg shadow-md p-6 border ${getScoreBg(kpis.review_sla_hit_rate)}`}>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">
            Review SLA Hit Rate
          </h3>
          <p className={`text-4xl font-bold ${getScoreColor(kpis.review_sla_hit_rate)}`}>
            {(kpis.review_sla_hit_rate * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Within target timeframe
          </p>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">
            Red Team Security
          </h3>
          <div className={`rounded p-3 border ${getScoreBg(kpis.redteam_pass_rate)}`}>
            <p className="text-xs text-gray-600 mb-1">Pass Rate</p>
            <p className={`text-2xl font-bold ${getScoreColor(kpis.redteam_pass_rate)}`}>
              {(kpis.redteam_pass_rate * 100).toFixed(1)}%
            </p>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            Higher is better - system blocks attacks
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">
            HITL Queue
          </h3>
          <div className={`rounded p-3 border ${
            kpis.hitl_queue_size === 0 ? "bg-green-50 border-green-200" :
            kpis.hitl_queue_size < 5 ? "bg-yellow-50 border-yellow-200" :
            "bg-red-50 border-red-200"
          }`}>
            <p className="text-xs text-gray-600 mb-1">Pending Approvals</p>
            <p className={`text-2xl font-bold ${
              kpis.hitl_queue_size === 0 ? "text-green-600" :
              kpis.hitl_queue_size < 5 ? "text-yellow-600" :
              "text-red-600"
            }`}>
              {kpis.hitl_queue_size}
            </p>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            Items awaiting human review
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">
            Processing Volume
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">Total Runs</span>
              <span className="font-bold text-blue-600">{kpis.total_runs}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">Completed</span>
              <span className="font-bold text-green-600">{kpis.completed_runs}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">Documents</span>
              <span className="font-bold text-purple-600">{kpis.total_documents}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">
          Detailed Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Accuracy & Quality
            </h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Clause Extraction</span>
                  <span className="font-medium">{(kpis.clause_extraction_accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      kpis.clause_extraction_accuracy >= 0.9 ? "bg-green-600" :
                      kpis.clause_extraction_accuracy >= 0.7 ? "bg-yellow-600" :
                      "bg-red-600"
                    }`}
                    style={{ width: `${kpis.clause_extraction_accuracy * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">PII Detection (F1)</span>
                  <span className="font-medium">{(kpis.pii_f1_score * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      kpis.pii_f1_score >= 0.9 ? "bg-green-600" :
                      kpis.pii_f1_score >= 0.7 ? "bg-yellow-600" :
                      "bg-red-600"
                    }`}
                    style={{ width: `${kpis.pii_f1_score * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Security & Compliance
            </h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Red Team Pass Rate</span>
                  <span className="font-medium">{(kpis.redteam_pass_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      kpis.redteam_pass_rate >= 0.9 ? "bg-green-600" :
                      kpis.redteam_pass_rate >= 0.7 ? "bg-yellow-600" :
                      "bg-red-600"
                    }`}
                    style={{ width: `${kpis.redteam_pass_rate * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Review SLA Hit Rate</span>
                  <span className="font-medium">{(kpis.review_sla_hit_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      kpis.review_sla_hit_rate >= 0.9 ? "bg-green-600" :
                      kpis.review_sla_hit_rate >= 0.7 ? "bg-yellow-600" :
                      "bg-red-600"
                    }`}
                    style={{ width: `${kpis.review_sla_hit_rate * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Summary */}
      <div className="mt-6 bg-gray-100 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">
          Audit & Compliance Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded p-3">
            <p className="text-xs text-gray-600 mb-1">Total Audit Logs</p>
            <p className="text-2xl font-bold text-gray-800">{kpis.total_audit_logs}</p>
          </div>
          <div className="bg-white rounded p-3">
            <p className="text-xs text-gray-600 mb-1">Unauthorized Disclosures</p>
            <p className={`text-2xl font-bold ${kpis.unauthorized_disclosures === 0 ? "text-green-600" : "text-red-600"}`}>
              {kpis.unauthorized_disclosures}
            </p>
          </div>
          <div className="bg-white rounded p-3">
            <p className="text-xs text-gray-600 mb-1">HITL Approvals</p>
            <p className="text-2xl font-bold text-yellow-600">{kpis.hitl_queue_size}</p>
          </div>
          <div className="bg-white rounded p-3">
            <p className="text-xs text-gray-600 mb-1">Documents Processed</p>
            <p className="text-2xl font-bold text-purple-600">{kpis.total_documents}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

