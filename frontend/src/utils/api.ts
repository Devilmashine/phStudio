import axios from 'axios';

const API_URL = '/api'; // Use relative URL to work with Vite proxy

export const bookingApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Можно добавить interceptors для обработки токенов или ошибок
bookingApi.interceptors.response.use(
  (response) => response,
  (error) => {
    // Глобальная обработка ошибок
    return Promise.reject(error);
  }
);
