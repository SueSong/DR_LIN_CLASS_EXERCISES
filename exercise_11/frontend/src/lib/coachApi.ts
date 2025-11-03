import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8011';

export const coachAPI = {
  async startSession(parentName: string) {
    const res = await axios.post(`${API_URL}/api/coach/start`, { parent_name: parentName });
    return res.data as { session_id: string; message: string };
  },
};

export default coachAPI;


