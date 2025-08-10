import axios from 'axios';
import { ENV } from '../config/env';
import authService from './authService';

const api = axios.create({
  baseURL: ENV.API_URL,
});

api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// We can also add a response interceptor to handle token refresh logic globally
// For now, this is sufficient.

export default api;
