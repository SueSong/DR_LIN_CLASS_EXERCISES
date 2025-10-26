import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CallResponse {
  call_id: string;
  status: string;
  message: string;
  matched: boolean;
  partner_name?: string;
}

export interface CallStats {
  active_calls: number;
  waiting_customers: number;
  available_agents: number;
}

export const callAPI = {
  // Start a new call (agent or customer)
  async startCall(userType: 'agent' | 'customer', userName: string): Promise<CallResponse> {
    const response = await axios.post(`${API_URL}/api/calls/start`, {
      user_type: userType,
      user_name: userName
    });
    return response.data;
  },

  // Get call status
  async getStatus(callId: string) {
    const response = await axios.get(`${API_URL}/api/calls/status/${callId}`);
    return response.data;
  },

  // End a call
  async endCall(callId: string) {
    const response = await axios.post(`${API_URL}/api/calls/end/${callId}`);
    return response.data;
  },

  // Get call center statistics
  async getStats(): Promise<CallStats> {
    const response = await axios.get(`${API_URL}/api/calls/stats`);
    return response.data;
  },

  // Get partner's call ID for routing
  async getPartner(callId: string) {
    const response = await axios.get(`${API_URL}/api/calls/match/${callId}`);
    return response.data;
  }
};

export default callAPI;

