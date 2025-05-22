import { useState, useCallback } from 'react';

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

export const useApi = <T>() => {
  const [response, setResponse] = useState<ApiResponse<T>>({
    data: null,
    error: null,
    loading: false,
  });

  const fetchData = useCallback(async (url: string, options: RequestInit = {}) => {
    setResponse(prev => {
      if (
        prev.loading === true &&
        prev.error === null &&
        JSON.stringify(prev.data) === JSON.stringify(null)
      ) {
        return prev; // Избегаем лишнего обновления
      }
      return { ...prev, loading: true, error: null };
    });

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      };

      const apiUrl = process.env.VITE_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}${url}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResponse(prev => {
        if (
          JSON.stringify(prev.data) === JSON.stringify(data) &&
          prev.error === null &&
          prev.loading === false
        ) {
          return prev; // Избегаем лишнего обновления
        }
        return { data, error: null, loading: false };
      });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Произошла ошибка';
      setResponse(prev => {
        if (
          prev.error === errorMessage &&
          prev.data === null &&
          prev.loading === false
        ) {
          return prev; // Избегаем лишнего обновления
        }
        return { data: null, error: errorMessage, loading: false };
      });
      throw error;
    }
  }, []);

  return { ...response, fetchData };
};