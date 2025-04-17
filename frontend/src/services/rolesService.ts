import { Role } from '../types/roles';

const API_URL = '/api/roles';

export async function fetchRoles(): Promise<Role[]> {
  const res = await fetch(API_URL, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки ролей');
  return res.json();
}

export async function createRole(role: Omit<Role, 'id'>): Promise<Role> {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(role)
  });
  if (!res.ok) throw new Error('Ошибка создания роли');
  return res.json();
}

export async function updateRole(role: Role): Promise<Role> {
  const res = await fetch(`${API_URL}/${role.id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(role)
  });
  if (!res.ok) throw new Error('Ошибка обновления роли');
  return res.json();
}

export async function deleteRole(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка удаления роли');
} 