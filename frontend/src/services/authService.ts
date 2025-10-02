import api from './api';
import { decodeJwt } from 'jose';

const API_URL = `/auth`;  // Removed /api prefix since it's already in the base URL

interface DecodedToken {
  sub: string;
  role: 'admin' | 'manager' | 'user';
  exp: number;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'manager' | 'user';
  ical_token?: string | null;
}

// Secure token management without localStorage
let currentUser: UserProfile | null = null;
let accessToken: string | null = null;

const storeUserProfile = (profile: UserProfile) => {
  sessionStorage.setItem('user', JSON.stringify(profile));
  localStorage.setItem('user', JSON.stringify(profile));
};

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
    currentUser = {
      id: -1,
      username: decoded.sub,
      email: '',
      role: decoded.role,
    } as UserProfile;

    try {
      const profileResponse = await api.get<UserProfile>(`${API_URL}/users/me`);
      currentUser = profileResponse.data;
      storeUserProfile(currentUser);
    } catch (profileError) {
      console.warn('Failed to load user profile after login:', profileError);
      storeUserProfile(currentUser);
    }
  }
  return response.data;
};

const logout = async () => {
  // Clear memory
  accessToken = null;
  currentUser = null;
  
  // Clear sessionStorage
  sessionStorage.removeItem('user');
  localStorage.removeItem('user');
  
  // Call logout endpoint to clear httpOnly cookie
  try {
    await api.post(`${API_URL}/logout`, {}, { withCredentials: true });
  } catch (error) {
    console.warn('Logout endpoint error:', error);
  }
};

const getCurrentUser = (): UserProfile | null => {
  if (currentUser) return currentUser;
  
  // Try to restore from sessionStorage/localStorage on page refresh
  const userStr = sessionStorage.getItem('user') ?? localStorage.getItem('user');
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
      currentUser = {
        id: -1,
        username: decoded.sub,
        email: '',
        role: decoded.role,
      } as UserProfile;

      try {
        const profileResponse = await api.get<UserProfile>(`${API_URL}/users/me`);
        currentUser = profileResponse.data;
      } catch (profileError) {
        console.warn('Failed to refresh user profile:', profileError);
      }

      storeUserProfile(currentUser);
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