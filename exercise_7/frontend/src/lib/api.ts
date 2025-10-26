import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8002'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API Types
export interface HealthResponse {
  status: string
  service: string
  version: string
  environment: string
  timestamp: string
  dependencies?: {
    database?: {
      status: string
      details?: any
    }
    chromadb?: {
      status: string
      url?: string
      api_version?: string
    }
  }
}

export interface DocumentUploadResponse {
  id: string
  filename: string
  status: string
  message: string
}

export interface QAPair {
  id: string
  question: string
  answer: string
  tags?: string[]
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: {
    knowledge_base_hits: Array<{
      id: string
      content: string
      filename: string
      similarity_score: number
    }>
    qa_hits: Array<{
      id: string
      question: string
      answer: string
      similarity_score: number
    }>
  }
}

export interface ChatResponse {
  id: string
  message: string
  response: string
  sources: Array<{
    document_id: string
    filename: string
    chunk_text: string
    similarity_score: number
    page_number?: number
  }>
  qa_matches: Array<{
    question: string
    answer: string
    similarity_score: number
  }>
  timestamp: string
  processing_time_ms: number
  model_used: string
}

// API Functions
export const api = {
  // Health check
  getHealth: (): Promise<HealthResponse> => 
    apiClient.get('/health/detailed'),

  // Knowledge Base
  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getDocuments: async () => {
    const response = await apiClient.get('/api/v1/documents')
    return response.data || []
  },

  deleteDocument: (id: string) => 
    apiClient.delete(`/api/v1/documents/${id}`),

  // Q&A Management
  getQAPairs: async (): Promise<QAPair[]> => {
    const response = await apiClient.get('/api/v1/qa-pairs')
    return response.data || []
  },

  createQAPair: async (data: { question: string; answer: string; tags?: string[] }): Promise<QAPair> => {
    const response = await apiClient.post('/api/v1/qa-pairs', data)
    return response.data
  },

  updateQAPair: (id: string, data: Partial<QAPair>): Promise<QAPair> => 
    apiClient.put(`/api/v1/qa-pairs/${id}`, data),

  deleteQAPair: (id: string) => 
    apiClient.delete(`/api/v1/qa-pairs/${id}`),

  // Chat
  sendMessage: async (message: string, sessionId?: string): Promise<ChatResponse> => {
    const response = await apiClient.post('/api/v1/chat', {
      message,
      session_id: sessionId,
    })
    return response.data
  },

  getChatHistory: (sessionId: string): Promise<ChatMessage[]> => 
    apiClient.get(`/api/v1/chat/history/${sessionId}`),

  // Test endpoints
  testDatabase: () => 
    apiClient.get('/test/database'),

  testChromaDB: () => 
    apiClient.get('/test/chromadb'),

  // Exercise 7: Agents endpoints (scaffold)
  agentsRun: (query: string, overrides?: Record<string, any>) =>
    apiClient.post('/api/agents/run', { query, overrides }),

  getTrace: (traceId: string) =>
    apiClient.get(`/api/agents/trace/${traceId}`),

  replayTrace: (traceId: string) =>
    apiClient.post(`/api/agents/replay/${traceId}`),

  switchPrompt: (name: string, version: number) =>
    apiClient.post(`/api/agents/prompt/switch`, null, { params: { name, v: version } }),

  getCostReport: (params?: { from?: string; to?: string }) =>
    apiClient.get('/api/agents/report/cost', { params }),

  // Prompt management
  listPromptVersions: (promptId: string) =>
    apiClient.get(`/api/prompts/${encodeURIComponent(promptId)}/versions`),

  createPromptVersion: (promptId: string, payload: { template: string; metadata?: any; changelog?: string; created_by?: string }) =>
    apiClient.post(`/api/prompts/${encodeURIComponent(promptId)}`, payload),

  deployPrompt: (promptId: string, payload: { env: string; strategy: 'fixed' | 'ab'; active_version?: number; ab_alt_version?: number; traffic_split?: number }) =>
    apiClient.post(`/api/prompts/${encodeURIComponent(promptId)}/deploy`, payload),

  resolvePrompt: (promptUri: string, env = 'development', userKey?: string) =>
    apiClient.get('/api/prompts/resolve', { params: { prompt: promptUri, env, user_key: userKey } }),
}
