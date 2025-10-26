const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload document");
  }

  return response.json();
}

export async function listDocuments() {
  const response = await fetch(`${API_BASE_URL}/api/documents`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch documents");
  }

  return response.json();
}

export async function getDocument(docId: string) {
  const response = await fetch(`${API_BASE_URL}/api/documents/${docId}`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch document");
  }

  return response.json();
}

export async function startReviewRun(docId: string, policyIds?: string[], options?: any) {
  const response = await fetch(`${API_BASE_URL}/api/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      doc_id: docId,
      policy_ids: policyIds,
      options: options,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to start review run");
  }

  return response.json();
}

export async function getRun(runId: string) {
  const response = await fetch(`${API_BASE_URL}/api/run/${runId}`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch run");
  }

  return response.json();
}

export async function listPolicies() {
  const response = await fetch(`${API_BASE_URL}/api/policies`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch policies");
  }

  return response.json();
}

export async function getHITLQueue() {
  const response = await fetch(`${API_BASE_URL}/api/hitl/queue`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch HITL queue");
  }

  return response.json();
}

export async function getHITLDetails(hitlId: string) {
  const response = await fetch(`${API_BASE_URL}/api/hitl/${hitlId}`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch HITL details");
  }

  return response.json();
}

export async function respondToHITL(hitlId: string, decisions: any[]) {
  const response = await fetch(`${API_BASE_URL}/api/hitl/${hitlId}/respond`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      hitl_id: hitlId,
      decisions: decisions,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to respond to HITL");
  }

  return response.json();
}

export async function runRedTeamTest(test: any) {
  const response = await fetch(`${API_BASE_URL}/api/redteam/test`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(test),
  });

  if (!response.ok) {
    throw new Error("Failed to run red team test");
  }

  return response.json();
}

export async function listRedTeamTests() {
  const response = await fetch(`${API_BASE_URL}/api/redteam/tests`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch red team tests");
  }

  return response.json();
}

export async function getKPIs() {
  const response = await fetch(`${API_BASE_URL}/api/reports/kpis`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch KPIs");
  }

  return response.json();
}

export async function getAuditLogs(limit: number = 100) {
  const response = await fetch(`${API_BASE_URL}/api/audit/logs?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch audit logs");
  }

  return response.json();
}

export async function exportRedline(runId: string, format: string = "md") {
  const response = await fetch(`${API_BASE_URL}/api/export/run/${runId}/redline?format=${format}`);
  
  if (!response.ok) {
    throw new Error("Failed to export redline");
  }

  return response.json();
}

export async function exportFinal(runId: string) {
  const response = await fetch(`${API_BASE_URL}/api/export/run/${runId}/final`);
  
  if (!response.ok) {
    throw new Error("Failed to export final document");
  }

  return response.json();
}

