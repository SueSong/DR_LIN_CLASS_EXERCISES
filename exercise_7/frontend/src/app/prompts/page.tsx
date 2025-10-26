"use client"

import React, { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function PromptsPage() {
  const [promptId, setPromptId] = useState('agent/planner')
  const [versions, setVersions] = useState<any[]>([])
  const [template, setTemplate] = useState('')
  const [changelog, setChangelog] = useState('')
  const [strategy, setStrategy] = useState<'fixed' | 'ab'>('fixed')
  const [activeVersion, setActiveVersion] = useState<number | undefined>(undefined)
  const [abAltVersion, setAbAltVersion] = useState<number | undefined>(undefined)
  const [trafficSplit, setTrafficSplit] = useState<number>(10)
  const [loading, setLoading] = useState(false)

  async function refresh() {
    if (!promptId) return
    const res = await api.listPromptVersions(promptId)
    setVersions(res.versions || [])
  }

  useEffect(() => {
    refresh().catch(() => {})
  }, [promptId])

  async function createVersion() {
    setLoading(true)
    try {
      await api.createPromptVersion(promptId, { template, changelog, created_by: 'instructor' })
      setTemplate('')
      setChangelog('')
      await refresh()
    } finally {
      setLoading(false)
    }
  }

  async function deploy() {
    setLoading(true)
    try {
      await api.deployPrompt(promptId, {
        env: 'development',
        strategy,
        active_version: activeVersion,
        ab_alt_version: abAltVersion,
        traffic_split: strategy === 'ab' ? trafficSplit : 0,
      })
      alert('Deploy updated')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Prompt Management</h1>

      <div className="p-4 border rounded bg-white space-y-3">
        <div className="flex gap-3 items-end">
          <label className="flex-1">
            <span className="text-sm">Prompt ID</span>
            <input className="w-full border rounded p-2" value={promptId} onChange={e => setPromptId(e.target.value)} />
          </label>
          <button onClick={refresh} className="px-3 py-2 bg-gray-200 rounded">Refresh</button>
        </div>

        <div>
          <h2 className="font-medium mb-2">Versions</h2>
          <div className="max-h-72 overflow-auto border rounded">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2">Version</th>
                  <th className="p-2">Created</th>
                  <th className="p-2">Changelog</th>
                </tr>
              </thead>
              <tbody>
                {versions.map(v => (
                  <tr key={v.version} className="border-t">
                    <td className="p-2">{v.version}</td>
                    <td className="p-2">{v.created_at}</td>
                    <td className="p-2">{v.changelog}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="p-4 border rounded bg-white space-y-3">
        <h2 className="font-medium">Create New Version</h2>
        <label className="block">
          <span className="text-sm">Template</span>
          <textarea className="w-full border rounded p-2 h-40" value={template} onChange={e => setTemplate(e.target.value)} />
        </label>
        <label className="block">
          <span className="text-sm">Changelog</span>
          <input className="w-full border rounded p-2" value={changelog} onChange={e => setChangelog(e.target.value)} />
        </label>
        <button disabled={loading || !template} onClick={createVersion} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50">Create Version</button>
      </div>

      <div className="p-4 border rounded bg-white space-y-3">
        <h2 className="font-medium">Deploy</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <label className="block">
            <span className="text-sm">Strategy</span>
            <select className="w-full border rounded p-2" value={strategy} onChange={e => setStrategy(e.target.value as any)}>
              <option value="fixed">fixed</option>
              <option value="ab">ab</option>
            </select>
          </label>
          <label className="block">
            <span className="text-sm">Active Version</span>
            <input type="number" className="w-full border rounded p-2" value={activeVersion ?? ''} onChange={e => setActiveVersion(e.target.value ? parseInt(e.target.value) : undefined)} />
          </label>
          {strategy === 'ab' && (
            <>
              <label className="block">
                <span className="text-sm">Alt Version</span>
                <input type="number" className="w-full border rounded p-2" value={abAltVersion ?? ''} onChange={e => setAbAltVersion(e.target.value ? parseInt(e.target.value) : undefined)} />
              </label>
              <label className="block">
                <span className="text-sm">Traffic %</span>
                <input type="number" className="w-full border rounded p-2" value={trafficSplit} onChange={e => setTrafficSplit(parseInt(e.target.value || '0'))} />
              </label>
            </>
          )}
        </div>
        <button disabled={loading} onClick={deploy} className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50">Update Deploy</button>
      </div>
    </div>
  )
}
