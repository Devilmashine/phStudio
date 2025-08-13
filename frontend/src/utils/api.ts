import axios from 'axios';

const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-production-api-url.com/api' // Заменить на реальный URL
  : 'http://localhost:8000/api'; // Для локальной разработки

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
