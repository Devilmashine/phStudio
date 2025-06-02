import { User } from './usersService';

const API_URL = '/api/me';

export async function fetchCurrentUser(): Promise<User> {
  const res = await fetch(API_URL, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка получения текущего пользователя');
  return res.json();
}

export function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem('token'));
}

export function getCurrentUserRole(): string | null {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try {
    const user = JSON.parse(userStr);
    return user.role || null;
  } catch {
    return null;
  }
}