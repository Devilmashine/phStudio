export interface Client {
  id: number;
  name: string;
  phone: string;
  email?: string;
  notes?: string;
  created_at: string;
}

const API_URL = '/api/clients';

export async function fetchClients(): Promise<Client[]> {
  const res = await fetch(API_URL, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки клиентов');
  return res.json();
}

export async function fetchClient(id: number): Promise<Client> {
  const res = await fetch(`${API_URL}/${id}`, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки клиента');
  return res.json();
}

export async function createClient(data: Omit<Client, 'id' | 'created_at'>): Promise<Client> {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Ошибка создания клиента');
  return res.json();
}

export async function updateClient(id: number, data: Partial<Client>): Promise<Client> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Ошибка обновления клиента');
  return res.json();
}

export async function deleteClient(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка удаления клиента');
}
