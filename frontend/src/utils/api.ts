import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  login: (email: string, password: string) => 
    api.post('/auth/login', null, { params: { email, password } }),
  register: (data: any) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

// Issue report endpoints
export const reportsAPI = {
  create: (data: any) => api.post('/reports', data),
  list: (params?: any) => api.get('/reports', { params }),
  getById: (id: number) => api.get(`/reports/${id}`),
  update: (id: number, data: any) => api.put(`/reports/${id}`, data),
  mergeDuplicates: (primaryId: number, duplicateId: number) => 
    api.post(`/reports/${primaryId}/merge/${duplicateId}`),
  getAITriage: (id: number) => api.get(`/reports/ai/triage/${id}`),
};

// Dashboard endpoints
export const dashboardAPI = {
  getStats: (wardId?: number) => api.get('/dashboard/stats', { params: { ward_id: wardId } }),
};
