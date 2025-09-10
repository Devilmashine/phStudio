import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ENV } from '../config/env';

const api = axios.create({
  baseURL: ENV.API_URL,
  withCredentials: true, // Important for httpOnly cookies
  timeout: 30000, // Increased to 30 second timeout to prevent ETIMEDOUT errors
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

api.interceptors.request.use(
  async (config: AxiosRequestConfig) => {
    // Import authService dynamically to avoid circular dependency
    const { default: authService } = await import('./authService');
    
    const token = authService.getToken();
    if (token) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add CSRF protection header
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with automatic token refresh
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If refresh is already in progress, queue the request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          if (originalRequest.headers) {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
          }
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        // Import authService dynamically to avoid circular dependency
        const { default: authService } = await import('./authService');
        
        const refreshSuccess = await authService.refreshToken();
        if (refreshSuccess) {
          const newToken = authService.getToken();
          processQueue(null, newToken);
          
          if (originalRequest.headers && newToken) {
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          }
          
          return api(originalRequest);
        } else {
          processQueue(error, null);
          // Redirect to login or handle logout
          window.location.href = '/login';
          return Promise.reject(error);
        }
      } catch (refreshError) {
        processQueue(refreshError, null);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;