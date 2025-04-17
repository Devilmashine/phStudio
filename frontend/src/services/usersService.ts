import { Role } from '../types/roles';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  full_name: string;
  created_at: string;
  last_login: string;
}

const API_URL = '/api/users';

export async function fetchUsers(): Promise<User[]> {
  const res = await fetch(API_URL, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки пользователей');
  return res.json();
}

export async function changeUserRole(userId: number, role: string): Promise<User> {
  const res = await fetch(`${API_URL}/${userId}/role`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ role })
  });
  if (!res.ok) throw new Error('Ошибка смены роли пользователя');
  return res.json();
}

export async function deleteUser(userId: number): Promise<void> {
  const res = await fetch(`${API_URL}/${userId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка удаления пользователя');
} 