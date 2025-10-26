const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  message: string;
  conversation_id?: string;
  document_ids?: string[];
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  blocked: boolean;
  security_scan: {
    threats_detected: boolean;
    threat_count: number;
    threats: any[];
    risk_score: number;
  };
  timestamp: string;
}

export async function sendChatMessage(message: ChatMessage): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(message),
  });

  if (!response.ok) {
    throw new Error("Failed to send message");
  }

  return response.json();
}

export async function listConversations() {
  const response = await fetch(`${API_BASE_URL}/api/chat/conversations`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch conversations");
  }

  return response.json();
}

export async function getConversation(conversationId: string) {
  const response = await fetch(`${API_BASE_URL}/api/chat/conversations/${conversationId}`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch conversation");
  }

  return response.json();
}

export async function getChatSecurityEvents() {
  const response = await fetch(`${API_BASE_URL}/api/chat/security-events`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch security events");
  }

  return response.json();
}

