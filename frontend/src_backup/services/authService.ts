import api from './api';
import { decodeJwt } from 'jose';

const API_URL = `/auth`;  // Removed /api prefix since it's already in the base URL

interface DecodedToken {
  sub: string;
  role: 'admin' | 'manager' | 'user';
  exp: number;
}

interface User {
  username: string;
  role: 'admin' | 'manager' | 'user';
}

// Secure token management without localStorage
let currentUser: User | null = null;
let accessToken: string | null = null;

const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  const response = await api.post(`${API_URL}/token`, params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    withCredentials: true, // Important for httpOnly cookies
  });

  if (response.data.access_token) {
    accessToken = response.data.access_token;
    const decoded = decodeJwt<DecodedToken>(accessToken);
    currentUser = { username: decoded.sub, role: decoded.role };
    
    // Store only non-sensitive user info in sessionStorage (cleared on tab close)
    sessionStorage.setItem('user', JSON.stringify(currentUser));
  }
  return response.data;
};

const logout = async () => {
  // Clear memory
  accessToken = null;
  currentUser = null;
  
  // Clear sessionStorage
  sessionStorage.removeItem('user');
  
  // Call logout endpoint to clear httpOnly cookie
  try {
    await api.post(`${API_URL}/logout`, {}, { withCredentials: true });
  } catch (error) {
    console.warn('Logout endpoint error:', error);
  }
};

const getCurrentUser = (): User | null => {
  if (currentUser) return currentUser;
  
  // Try to restore from sessionStorage on page refresh
  const userStr = sessionStorage.getItem('user');
  if (userStr) {
    try {
      currentUser = JSON.parse(userStr);
      return currentUser;
    } catch {
      sessionStorage.removeItem('user');
    }
  }
  return null;
};

const getToken = (): string | null => {
  return accessToken;
};

// Auto-refresh token functionality
const refreshToken = async (): Promise<boolean> => {
  try {
    const response = await api.post(`${API_URL}/refresh`, {}, {
      withCredentials: true,
    });
    
    if (response.data.access_token) {
      accessToken = response.data.access_token;
      const decoded = decodeJwt<DecodedToken>(accessToken);
      currentUser = { username: decoded.sub, role: decoded.role };
      sessionStorage.setItem('user', JSON.stringify(currentUser));
      return true;
    }
  } catch (error) {
    console.warn('Token refresh failed:', error);
    await logout();
  }
  return false;
};

// Check if token is expired or expiring soon
const isTokenExpired = (): boolean => {
  if (!accessToken) return true;
  
  try {
    const decoded = decodeJwt<DecodedToken>(accessToken);
    const now = Math.floor(Date.now() / 1000);
    // Consider token expired if it expires in less than 5 minutes
    return decoded.exp < (now + 300);
  } catch {
    return true;
  }
};

const authService = {
  login,
  logout,
  getCurrentUser,
  getToken,
  refreshToken,
  isTokenExpired,
};

export default authService;