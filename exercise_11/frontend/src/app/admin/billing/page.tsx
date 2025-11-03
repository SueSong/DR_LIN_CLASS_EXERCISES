"use client";

import { useState, useEffect } from 'react';
import { Download, Eye, X, FileText } from 'lucide-react';

interface DailyStats {
  date: string;
  total_turns: number;
  total_cost_usd: number;
  total_input_tokens: number;
  total_output_tokens: number;
  full_mode_turns: number;
  lite_mode_turns: number;
  over_budget_turns: number;
  budget_limit_usd: number;
  budget_remaining_usd: number;
  is_over_budget: boolean;
  current_cost_usd: number;
}

interface BudgetStatus {
  is_over_budget: boolean;
  current_cost_usd: number;
  budget_limit_usd: number;
  budget_remaining_usd: number;
  budget_used_percent: number;
  date: string;
}

interface SparklineData {
  days: number;
  start_date: string;
  end_date: string;
  data: number[];
  labels: string[];
}

interface CSVRecord {
  turn_id: string;
  session_id: string;
  timestamp: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost_usd: number;
  model_mode: string;
  was_over_budget: boolean;
}

interface CSVPreview {
  date: string;
  total_records: number;
  stats: DailyStats;
  records: CSVRecord[];
}

export default function BillingAdminPage() {
  const [dailyStats, setDailyStats] = useState<DailyStats | null>(null);
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus | null>(null);
  const [sparklineData, setSparklineData] = useState<SparklineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newBudget, setNewBudget] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<CSVPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [reportDate, setReportDate] = useState<string>('');

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch daily stats
      const statsRes = await fetch('http://localhost:8011/api/billing/daily');
      const stats = await statsRes.json();
      setDailyStats(stats);
      
      // Fetch budget status
      const budgetRes = await fetch('http://localhost:8011/api/billing/budget/status');
      const budget = await budgetRes.json();
      setBudgetStatus(budget);
      
      // Fetch sparkline data (last 7 days)
      const sparklineRes = await fetch('http://localhost:8011/api/billing/sparkline?days=7');
      const sparkline = await sparklineRes.json();
      setSparklineData(sparkline);
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load billing data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Handle Escape key to close preview modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showPreview) {
        setShowPreview(false);
      }
    };
    
    if (showPreview) {
      window.addEventListener('keydown', handleEscape);
      return () => window.removeEventListener('keydown', handleEscape);
    }
  }, [showPreview]);

  useEffect(() => {
    // Set default report date to today
    if (!reportDate) {
      const today = new Date().toISOString().split('T')[0];
      setReportDate(today);
    }
  }, []);

  const handleSetBudget = async () => {
    const budgetValue = parseFloat(newBudget);
    if (isNaN(budgetValue) || budgetValue <= 0) {
      alert('Please enter a valid budget amount');
      return;
    }

    try {
      const res = await fetch('http://localhost:8011/api/billing/budget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ daily_budget_usd: budgetValue }),
      });

      if (res.ok) {
        setNewBudget('');
        fetchData();
        alert('Budget updated successfully');
      } else {
        alert('Failed to update budget');
      }
    } catch (err) {
      alert('Error updating budget');
    }
  };

  const handlePreviewReport = async () => {
    if (!reportDate) {
      alert('Please select a date');
      return;
    }

    setPreviewLoading(true);
    try {
      const res = await fetch(`http://localhost:8011/api/billing/report/preview/${reportDate}`);
      if (res.ok) {
        const data = await res.json();
        setPreviewData(data);
        setShowPreview(true);
      } else {
        alert('Failed to load report preview');
      }
    } catch (err) {
      alert('Error loading report preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!reportDate) {
      alert('Please select a date');
      return;
    }

    const url = `http://localhost:8011/api/billing/report/csv/${reportDate}`;
    window.open(url, '_blank');
  };

  const drawSparkline = (canvasId: string, data: number[], maxValue: number) => {
    const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
    if (!canvas || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const padding = 10;

    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();

    const stepX = (width - 2 * padding) / (data.length - 1 || 1);
    const scaleY = (height - 2 * padding) / maxValue;

    data.forEach((value, index) => {
      const x = padding + index * stepX;
      const y = height - padding - value * scaleY;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Fill area under curve
    ctx.lineTo(width - padding, height - padding);
    ctx.lineTo(padding, height - padding);
    ctx.closePath();
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
    ctx.fillStyle = gradient;
    ctx.fill();
  };

  useEffect(() => {
    if (sparklineData && sparklineData.data.length > 0) {
      const maxValue = Math.max(...sparklineData.data, 1);
      drawSparkline('sparkline-canvas', sparklineData.data, maxValue);
    }
  }, [sparklineData]);

  if (loading && !dailyStats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">Loading billing data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-slate-900 mb-8">Billing Dashboard</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            Error: {error}
          </div>
        )}

        {/* Budget Status Card */}
        {budgetStatus && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold text-slate-800 mb-4">Budget Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div>
                <div className="text-sm text-slate-600">Current Cost</div>
                <div className={`text-2xl font-bold ${budgetStatus.is_over_budget ? 'text-red-600' : 'text-green-600'}`}>
                  ${budgetStatus.current_cost_usd.toFixed(4)}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Budget Limit</div>
                <div className="text-2xl font-bold text-slate-800">
                  ${budgetStatus.budget_limit_usd.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Remaining</div>
                <div className="text-2xl font-bold text-blue-600">
                  ${budgetStatus.budget_remaining_usd.toFixed(4)}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Used</div>
                <div className="text-2xl font-bold text-slate-800">
                  {budgetStatus.budget_used_percent.toFixed(1)}%
                </div>
              </div>
            </div>

            {budgetStatus.is_over_budget && (
              <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
                <div className="text-red-800 font-semibold">⚠️ Daily Budget Exceeded</div>
                <div className="text-red-600 text-sm mt-1">
                  System is now operating in lite mode. Full mode will resume tomorrow.
                </div>
              </div>
            )}

            {/* Budget Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-4 mb-4">
              <div
                className={`h-4 rounded-full transition-all ${
                  budgetStatus.budget_used_percent >= 100
                    ? 'bg-red-500'
                    : budgetStatus.budget_used_percent >= 80
                    ? 'bg-yellow-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(100, budgetStatus.budget_used_percent)}%` }}
              />
            </div>

            {/* Set Budget Form */}
            <div className="flex gap-2">
              <input
                type="number"
                value={newBudget}
                onChange={(e) => setNewBudget(e.target.value)}
                placeholder="New daily budget (USD)"
                className="flex-1 px-4 py-2 border border-slate-300 rounded-lg"
              />
              <button
                onClick={handleSetBudget}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Update Budget
              </button>
            </div>
          </div>
        )}

        {/* Sparkline Chart */}
        {sparklineData && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold text-slate-800 mb-4">
              Cost Trend ({sparklineData.days} Days)
            </h2>
            <canvas
              id="sparkline-canvas"
              width="800"
              height="200"
              className="w-full"
            />
            <div className="text-sm text-slate-600 mt-2">
              {sparklineData.start_date} to {sparklineData.end_date}
            </div>
          </div>
        )}

        {/* Daily Statistics */}
        {dailyStats && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-slate-800 mb-4">
              Daily Statistics ({dailyStats.date})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="text-sm text-slate-600">Total Turns</div>
                <div className="text-3xl font-bold text-slate-900">
                  {dailyStats.total_turns.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Total Cost</div>
                <div className="text-3xl font-bold text-blue-600">
                  ${dailyStats.total_cost_usd.toFixed(4)}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Total Tokens</div>
                <div className="text-3xl font-bold text-slate-900">
                  {(dailyStats.total_input_tokens + dailyStats.total_output_tokens).toLocaleString()}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
              <div>
                <div className="text-sm text-slate-600">Full Mode Turns</div>
                <div className="text-xl font-semibold text-green-600">
                  {dailyStats.full_mode_turns}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Lite Mode Turns</div>
                <div className="text-xl font-semibold text-yellow-600">
                  {dailyStats.lite_mode_turns}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Over Budget Turns</div>
                <div className="text-xl font-semibold text-red-600">
                  {dailyStats.over_budget_turns}
                </div>
              </div>
              <div>
                <div className="text-sm text-slate-600">Input Tokens</div>
                <div className="text-xl font-semibold text-slate-800">
                  {dailyStats.total_input_tokens.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Daily Report Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h2 className="text-2xl font-semibold text-slate-800 mb-4">Daily Report</h2>
          
          <div className="flex gap-4 items-end mb-4">
            <div className="flex-1">
              <label className="block text-sm text-slate-600 mb-2">Select Date</label>
              <input
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              />
            </div>
            
            <button
              onClick={handlePreviewReport}
              disabled={previewLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
            >
              <Eye size={18} />
              {previewLoading ? 'Loading...' : 'Preview Report'}
            </button>
            
            <button
              onClick={handleDownloadReport}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <Download size={18} />
              Download CSV
            </button>
          </div>
        </div>

        {/* Preview Modal */}
        {showPreview && previewData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] flex flex-col">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b">
                <div>
                  <h3 className="text-2xl font-semibold text-slate-800">Report Preview</h3>
                  <p className="text-sm text-slate-600 mt-1">
                    {previewData.date} • {previewData.total_records} records
                  </p>
                </div>
                <button
                  onClick={() => setShowPreview(false)}
                  className="text-slate-500 hover:text-slate-700"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Preview Content */}
              <div className="overflow-auto flex-1 p-6">
                {/* Summary Stats */}
                <div className="grid grid-cols-4 gap-4 mb-6 p-4 bg-slate-50 rounded-lg">
                  <div>
                    <div className="text-sm text-slate-600">Total Turns</div>
                    <div className="text-xl font-bold text-slate-900">
                      {previewData.stats.total_turns}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-600">Total Cost</div>
                    <div className="text-xl font-bold text-blue-600">
                      ${previewData.stats.total_cost_usd.toFixed(4)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-600">Full Mode</div>
                    <div className="text-xl font-bold text-green-600">
                      {previewData.stats.full_mode_turns}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-600">Lite Mode</div>
                    <div className="text-xl font-bold text-yellow-600">
                      {previewData.stats.lite_mode_turns}
                    </div>
                  </div>
                </div>

                {/* Records Table */}
                {previewData.records.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-100">
                        <tr>
                          <th className="px-4 py-2 text-left">Turn ID</th>
                          <th className="px-4 py-2 text-left">Session ID</th>
                          <th className="px-4 py-2 text-left">Timestamp</th>
                          <th className="px-4 py-2 text-right">Input Tokens</th>
                          <th className="px-4 py-2 text-right">Output Tokens</th>
                          <th className="px-4 py-2 text-right">Total Tokens</th>
                          <th className="px-4 py-2 text-right">Cost (USD)</th>
                          <th className="px-4 py-2 text-center">Mode</th>
                          <th className="px-4 py-2 text-center">Over Budget</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewData.records.map((record, idx) => (
                          <tr key={idx} className="border-b hover:bg-slate-50">
                            <td className="px-4 py-2 font-mono text-xs">
                              {record.turn_id.substring(0, 12)}...
                            </td>
                            <td className="px-4 py-2 font-mono text-xs">
                              {record.session_id.substring(0, 12)}...
                            </td>
                            <td className="px-4 py-2 text-xs">
                              {new Date(record.timestamp).toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-right">
                              {record.input_tokens.toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-right">
                              {record.output_tokens.toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-right font-semibold">
                              {record.total_tokens.toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-right font-semibold text-blue-600">
                              ${record.cost_usd.toFixed(6)}
                            </td>
                            <td className="px-4 py-2 text-center">
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                record.model_mode === 'full' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {record.model_mode}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-center">
                              {record.was_over_budget ? (
                                <span className="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-800">
                                  Yes
                                </span>
                              ) : (
                                <span className="px-2 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-600">
                                  No
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <FileText size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No records found for this date</p>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-end gap-4 p-6 border-t">
                <button
                  onClick={() => setShowPreview(false)}
                  className="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    handleDownloadReport();
                    setShowPreview(false);
                  }}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <Download size={18} />
                  Download CSV
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 text-center">
          <button
            onClick={fetchData}
            className="px-6 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700"
          >
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
}

