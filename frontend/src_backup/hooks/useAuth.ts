import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      await authService.login(username, password);
      const user = authService.getCurrentUser();
      if (user?.role === 'admin') {
        navigate('/admin');
      } else if (user?.role === 'manager') {
        navigate('/manager');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during login.');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error('Logout failed', err);
    } finally {
      navigate('/login');
    }
  }, [navigate]);

  const isAuthenticated = () => {
    return !!authService.getToken();
  };

  return { login, logout, loading, error, isAuthenticated };
}
