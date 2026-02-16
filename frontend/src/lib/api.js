import axios from 'axios';

// API base URL - uses same domain in production
const API_BASE_URL = import.meta.env.PROD
  ? '/api'  // In production, proxy through nginx
  : 'http://localhost:8080/api';  // In development, direct to backend

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Athletes API
export const athletesAPI = {
  getAll: () => api.get('/athletes'),
  getOne: (id) => api.get(`/athletes/${id}`),
  create: (data) => api.post('/athletes', data),
  update: (id, data) => api.put(`/athletes/${id}`, data),
  delete: (id) => api.delete(`/athletes/${id}`),
};

// Meets API
export const meetsAPI = {
  getAll: () => api.get('/meets'),
  getOne: (id) => api.get(`/meets/${id}`),
  create: (data) => api.post('/meets', data),
};

// Results API
export const resultsAPI = {
  getAll: () => api.get('/results'),
  create: (data) => api.post('/results', data),
};

// Auth API (simple username/password check)
export const authAPI = {
  login: (username, password) => {
    // Simple auth - in production you'd validate against backend
    // For now, just check if credentials match hardcoded values
    if (username === 'ethanwells' && password === 'admin123') {
      const token = 'fake-jwt-token';
      const user = { username: 'ethanwells', name: 'Ethan Wells' };
      localStorage.setItem('auth_token', token);
      localStorage.setItem('auth_user', JSON.stringify(user));
      return Promise.resolve({ token, user });
    }
    return Promise.reject(new Error('Invalid username or password'));
  },
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    return Promise.resolve();
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  },
  getUser: () => {
    const userStr = localStorage.getItem('auth_user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

export default api;
