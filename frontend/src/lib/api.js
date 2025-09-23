import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  refresh: () => api.post('/auth/refresh'),
  getMe: () => api.get('/auth/me'),
};

// Profile API
export const profileAPI = {
  getProfile: () => api.get('/profiles/me'),
  createProfile: (profileData) => api.post('/profiles', profileData),
  updateProfile: (profileData) => api.put('/profiles/me', profileData),
  getDashboard: () => api.get('/profiles/me/dashboard'),
};

// Reports API
export const reportsAPI = {
  getReports: (params = {}) => api.get('/reports', { params }),
  getReport: (reportId) => api.get(`/reports/${reportId}`),
  generateReport: (reportData) => api.post('/reports/generate', reportData),
  downloadReport: (reportId) => api.get(`/reports/${reportId}/download`, {
    responseType: 'blob',
  }),
};

// Feedback API
export const feedbackAPI = {
  getFeedback: (params = {}) => api.get('/feedback', { params }),
  getPostFeedback: (postId) => api.get(`/feedback/${postId}`),
  getFeedbackSummary: () => api.get('/feedback/stats/summary'),
};

export default api;

