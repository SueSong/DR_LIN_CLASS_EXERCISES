"use client"
import React, { useState } from 'react'
import { api } from '@/lib/api'

export default function AgentConsolePage() {
  const [query, setQuery] = useState('what is the price of x?')
  const [failRate, setFailRate] = useState(0.35)
  const [budgetUsd, setBudgetUsd] = useState(0.05)
  const [model, setModel] = useState('gpt-4o-mini')
  const [injectTimeoutMs, setInjectTimeoutMs] = useState(0)
  const [cacheHitRate, setCacheHitRate] = useState(0.7)

  const [traceId, setTraceId] = useState<string>('')
  const [spans, setSpans] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  async function runTask() {
    setLoading(true)
    try {
      const overrides = {
        fail_rate: Number(failRate),
        budget_usd: Number(budgetUsd),
        model,
        inject_timeout_ms: Number(injectTimeoutMs),
        cache_hit_rate: Number(cacheHitRate),
      }
      const res = await api.agentsRun(query, overrides)
      const newTraceId = res.trace_id
      setTraceId(newTraceId)
      // poll once after a short delay
      setTimeout(async () => {
        const t = await api.getTrace(newTraceId)
        setSpans(t.spans || [])
      }, 800)
    } finally {
      setLoading(false)
    }
  }

  async function refreshTrace() {
    if (!traceId) return
    const t = await api.getTrace(traceId)
    setSpans(t.spans || [])
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Agent Console</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3 p-4 border rounded-md bg-white">
          <h2 className="font-medium">Run Controls</h2>
          <label className="block">
            <span className="text-sm">Query</span>
            <input className="w-full border rounded p-2" value={query} onChange={e => setQuery(e.target.value)} />
          </label>

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-sm">FAIL_RATE</span>
              <input type="number" step="0.01" className="w-full border rounded p-2" value={failRate} onChange={e => setFailRate(parseFloat(e.target.value))} />
            </label>
            <label className="block">
              <span className="text-sm">BUDGET_USD</span>
              <input type="number" step="0.01" className="w-full border rounded p-2" value={budgetUsd} onChange={e => setBudgetUsd(parseFloat(e.target.value))} />
            </label>
            <label className="block">
              <span className="text-sm">MODEL</span>
              <input className="w-full border rounded p-2" value={model} onChange={e => setModel(e.target.value)} />
            </label>
            <label className="block">
              <span className="text-sm">INJECT_TIMEOUT_MS</span>
              <input type="number" className="w-full border rounded p-2" value={injectTimeoutMs} onChange={e => setInjectTimeoutMs(parseInt(e.target.value || '0'))} />
            </label>
            <label className="block">
              <span className="text-sm">CACHE_HIT_RATE</span>
              <input type="number" step="0.01" className="w-full border rounded p-2" value={cacheHitRate} onChange={e => setCacheHitRate(parseFloat(e.target.value))} />
            </label>
          </div>

          <div className="flex items-center gap-3">
            <button onClick={runTask} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50">{loading ? 'Running…' : 'Run Plan'}</button>
            <button onClick={refreshTrace} className="px-4 py-2 bg-gray-200 rounded">Refresh Trace</button>
          </div>
        </div>

        <div className="space-y-2 p-4 border rounded-md bg-white">
          <h2 className="font-medium">Trace</h2>
          <div className="text-sm">Trace ID: <span className="font-mono">{traceId || '-'}</span></div>
          <div className="max-h-96 overflow-auto border rounded">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2">Span</th>
                  <th className="p-2">Parent</th>
                  <th className="p-2">Name</th>
                  <th className="p-2">Tool</th>
                  <th className="p-2">Latency(ms)</th>
                  <th className="p-2">Retry</th>
                  <th className="p-2">Err</th>
                </tr>
              </thead>
              <tbody>
                {spans.map((s: any) => (
                  <tr key={s.span_id} className="border-t">
                    <td className="p-2 font-mono text-xs">{s.span_id.slice(0,8)}</td>
                    <td className="p-2 font-mono text-xs">{s.parent_span_id ? s.parent_span_id.slice(0,8) : '-'}</td>
                    <td className="p-2">{s.name}</td>
                    <td className="p-2">{s.attributes?.tool_name || '-'}</td>
                    <td className="p-2">{s.attributes?.latency_ms ?? '-'}</td>
                    <td className="p-2">{s.attributes?.retry_count ?? 0}</td>
                    <td className="p-2 text-red-600">{s.attributes?.error_code || ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
