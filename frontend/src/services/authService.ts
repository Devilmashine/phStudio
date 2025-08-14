import api from './api';
import { decodeJwt } from 'jose';

const API_URL = `/api/auth`;

interface DecodedToken {
  sub: string;
  role: 'admin' | 'manager' | 'user';
  exp: number;
}

const login = async (username, password) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  const response = await api.post(`${API_URL}/token`, params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  if (response.data.access_token) {
    const token = response.data.access_token;
    localStorage.setItem('token', token);
    const decoded = decodeJwt<DecodedToken>(token);
    localStorage.setItem('user', JSON.stringify({ username: decoded.sub, role: decoded.role }));
  }
  return response.data;
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  return api.post(`${API_URL}/logout`, {});
};

const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) return JSON.parse(userStr);
  return null;
};

const getToken = () => {
  return localStorage.getItem('token');
};

const authService = {
  login,
  logout,
  getCurrentUser,
  getToken,
};

export default authService;
