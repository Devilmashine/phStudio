import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_LOGIN = '/api/token';
const API_REFRESH = '/api/refresh';
const API_LOGOUT = '/api/logout';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
        credentials: 'include', // важно для httpOnly cookie
      });
      if (!res.ok) throw new Error('Неверный логин или пароль');
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      // JWT exp декодируем для контроля срока жизни
      const payload = JSON.parse(atob(data.access_token.split('.')[1]));
      localStorage.setItem('token_exp', (payload.exp * 1000).toString());
      localStorage.setItem('role', payload.role);
      navigate('/admin');
    } catch (e: any) {
      setError(e.message || 'Ошибка авторизации');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await fetch(API_LOGOUT, { method: 'POST', credentials: 'include' });
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    localStorage.removeItem('token_exp');
    navigate('/login');
  };

  const isAuthenticated = () => {
    const token = localStorage.getItem('token');
    const exp = localStorage.getItem('token_exp');
    if (!token || !exp) return false;
    return Date.now() < parseInt(exp, 10);
  };

  const tryRefresh = async () => {
    try {
      const res = await fetch(API_REFRESH, {
        method: 'POST',
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Не удалось обновить сессию');
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      const payload = JSON.parse(atob(data.access_token.split('.')[1]));
      localStorage.setItem('token_exp', (payload.exp * 1000).toString());
      localStorage.setItem('role', payload.role);
      return true;
    } catch {
      await logout();
      return false;
    }
  };

  return { login, logout, loading, error, isAuthenticated, tryRefresh };
}

// Хелпер для авторизованных fetch-запросов с поддержкой refresh токена
export async function authFetch(input: RequestInfo, init: RequestInit = {}, tryRefresh?: () => Promise<boolean>): Promise<Response> {
  let token = localStorage.getItem('token');
  if (!init.headers) init.headers = {};
  (init.headers as any)['Authorization'] = `Bearer ${token}`;
  (init as any).credentials = 'include';
  let res = await fetch(input, init);
  if (res.status === 401 && tryRefresh) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      token = localStorage.getItem('token');
      (init.headers as any)['Authorization'] = `Bearer ${token}`;
      res = await fetch(input, init);
    }
  }
  return res;
}
