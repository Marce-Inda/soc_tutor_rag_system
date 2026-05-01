import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 45000, // 45 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Decision {
  accion: string;
  target: string;
  detalle?: string;
}

export interface Contexto {
  scenario_id?: string;
  tipo_incidente: string;
  fase: string;
  sistemas_afectados: string[];
}

export interface PlayerProfile {
  player_id: string;
  level: number;
  rol: string;
  language: string;
}

export interface QueueStatus {
  status: 'ACTIVE' | 'WAITING' | 'EXPIRED';
  position: number;
  codename: string;
  is_ready: boolean;
}

export async function getFeedback(decision: Decision, contexto: Contexto, playerProfile: PlayerProfile, userId: string = 'guest') {
  try {
    const response = await api.post(`/feedback?user_id=${userId}`, {
      decision,
      contexto,
      player_profile: playerProfile,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching feedback:', error);
    throw error;
  }
}

export async function getQueueStatus(userId: string): Promise<QueueStatus> {
  const response = await api.get(`/queue/status/${userId}`);
  return response.data;
}

export async function sendHeartbeat(userId: string) {
  const response = await api.post(`/queue/heartbeat/${userId}`);
  return response.data;
}

export async function checkHealth() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.warn('Backend connection failed');
    return null;
  }
}
