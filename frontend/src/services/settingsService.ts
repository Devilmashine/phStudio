export interface StudioSettings {
  id: number;
  name: string;
  address: string;
  phone: string;
  email: string;
  work_hours: string;
  description?: string;
}

const API_URL = '/settings/';  // Removed /api prefix since it's already in the base URL

export async function fetchSettings(): Promise<StudioSettings> {
  const token = localStorage.getItem('token');
  const res = await fetch(API_URL, {
    headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
  });
  if (!res.ok) throw new Error('Ошибка загрузки настроек');
  return res.json();
}

export async function updateSettings(data: Partial<StudioSettings>): Promise<StudioSettings> {
  const token = localStorage.getItem('token');
  const res = await fetch(API_URL, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Ошибка обновления настроек');
  return res.json();
}