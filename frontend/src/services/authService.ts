import { User } from './usersService';

const API_URL = '/api/me';

export async function fetchCurrentUser(): Promise<User> {
  const res = await fetch(API_URL, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка получения текущего пользователя');
  return res.json();
} 