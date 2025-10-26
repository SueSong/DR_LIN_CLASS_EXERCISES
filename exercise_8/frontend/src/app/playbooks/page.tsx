"use client";

import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { BookOpen, Plus, Trash2, Edit, Save, X } from "lucide-react";

interface Playbook {
  playbook_id: string;
  name: string;
  rules: any;
  created_at?: string;
}

export default function PlaybooksPage() {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [name, setName] = useState("");
  const [rulesText, setRulesText] = useState(
    JSON.stringify(
      {
        liability_cap: "12 months fees",
        data_retention: "90 days post-termination",
        indemnity_exclusions: ["force majeure", "third-party claims"],
        required_clauses: ["subprocessors", "audit rights", "SCC references"],
      },
      null,
      2
    )
  );
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const refresh = async () => {
    try {
      // Mock data - in real implementation, this would call api.listPlaybooks()
      // Keep existing playbooks in state
      setError(null);
    } catch (err) {
      setError("Failed to load playbooks");
      console.error(err);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) {
      setError("Playbook name is required");
      return;
    }

    try {
      const rules = JSON.parse(rulesText);
      // Mock create - in real implementation, this would call api.createPlaybook(name, rules)
      const newPlaybook = {
        playbook_id: `playbook_${Date.now()}`,
        name: name,
        rules: rules,
        created_at: new Date().toISOString(),
      };
      
      setPlaybooks(prevPlaybooks => [newPlaybook, ...prevPlaybooks]);
      setName("");
      setRulesText(
        JSON.stringify(
          {
            liability_cap: "12 months fees",
            data_retention: "90 days post-termination",
            indemnity_exclusions: ["force majeure", "third-party claims"],
            required_clauses: ["subprocessors", "audit rights", "SCC references"],
          },
          null,
          2
        )
      );
      setCreating(false);
      setError(null);
    } catch (err) {
      setError("Invalid JSON or failed to create playbook");
      console.error(err);
    }
  };

  const handleDelete = async (playbookId: string) => {
    if (!confirm("Are you sure you want to delete this playbook?")) return;

    try {
      // Mock delete - in real implementation, this would call api.deletePlaybook(playbookId)
      setPlaybooks(prevPlaybooks => prevPlaybooks.filter(p => p.playbook_id !== playbookId));
      setError(null);
    } catch (err) {
      setError("Failed to delete playbook");
      console.error(err);
    }
  };

  const formatRules = (rules: any) => {
    return JSON.stringify(rules, null, 2);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Playbooks</h1>
        <p className="text-gray-600">
          Define policy rules and guidelines for document review workflows
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-700 hover:text-red-900">
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Create New Playbook */}
      <div className="mb-8">
        {!creating ? (
          <button
            onClick={() => setCreating(true)}
            className="btn-primary flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create New Playbook
          </button>
        ) : (
          <div className="card bg-primary-50 border-2 border-primary-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Create New Playbook
            </h3>
            <div className="space-y-4">
              <div>
                <label className="label">Playbook Name</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Standard SaaS MSA Policy"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label className="label">Rules (JSON)</label>
                <textarea
                  className="input font-mono text-sm"
                  rows={12}
                  placeholder='{"liability_cap": "12 months fees"}'
                  value={rulesText}
                  onChange={(e) => setRulesText(e.target.value)}
                />
                <p className="text-xs text-gray-600 mt-1">
                  Define policy rules in JSON format
                </p>
              </div>
              <div className="flex space-x-3">
                <button onClick={handleCreate} className="btn-primary">
                  <Save className="w-4 h-4 mr-2 inline" />
                  Create Playbook
                </button>
                <button
                  onClick={() => {
                    setCreating(false);
                    setError(null);
                  }}
                  className="btn-secondary"
                >
                  <X className="w-4 h-4 mr-2 inline" />
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Playbooks List */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Existing Playbooks ({playbooks.length})
        </h2>

        {playbooks.length === 0 ? (
          <div className="card text-center py-12">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600">No playbooks created yet</p>
            <p className="text-sm text-gray-500 mt-2">
              Create your first playbook to define review policies
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {playbooks.map((playbook) => (
              <div
                key={playbook.playbook_id}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="bg-purple-100 p-3 rounded-lg">
                      <BookOpen className="w-6 h-6 text-purple-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {playbook.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                          {playbook.playbook_id}
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() =>
                        setEditingId(
                          editingId === playbook.playbook_id
                            ? null
                            : playbook.playbook_id
                        )
                      }
                      className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="View/Edit rules"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(playbook.playbook_id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete playbook"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {editingId === playbook.playbook_id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      Policy Rules
                    </h4>
                    <pre className="bg-gray-50 p-4 rounded-lg text-xs font-mono overflow-x-auto">
                      {formatRules(playbook.rules)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Example Playbook Templates */}
      <div className="mt-12 card bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Example Playbook Templates
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">SaaS MSA Policy</h4>
            <pre className="text-xs font-mono text-gray-700 overflow-x-auto">
              {JSON.stringify(
                {
                  liability_cap: "12 months fees",
                  payment_terms: "Net 30",
                  auto_renewal: true,
                  termination_notice: "90 days",
                },
                null,
                2
              )}
            </pre>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">GDPR DPA Policy</h4>
            <pre className="text-xs font-mono text-gray-700 overflow-x-auto">
              {JSON.stringify(
                {
                  data_retention: "90 days post-term",
                  required_clauses: ["SCC", "audit rights"],
                  subprocessor_approval: "prior written",
                  breach_notification: "72 hours",
                },
                null,
                2
              )}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
