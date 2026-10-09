import axios from 'axios';
import { normalizeFoundationResponse } from './foundationData';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
});

export async function getFoundation() {
  const response = await api.get('/fundacion');
  return normalizeFoundationResponse(response.data);
}

export async function postChatMessage(message) {
  const response = await api.post('/chat', { message });
  return response.data.response;
}