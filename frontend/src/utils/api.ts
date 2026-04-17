import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
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

export async function getFeedback(decision: Decision, contexto: Contexto, playerProfile: PlayerProfile) {
  try {
    const response = await api.post('/feedback', {
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

export async function checkHealth() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.warn('Backend connection failed');
    return null;
  }
}
