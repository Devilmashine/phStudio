export interface LogEntry {
  id: number;
  timestamp: string;
  user: string;
  action: string;
  details: string;
}

const API_URL = '/api/admin/logs';

export async function fetchLogs(params: { user?: string; date?: string } = {}): Promise<LogEntry[]> {
  let url = API_URL;
  const query = [];
  if (params.user) query.push(`user=${encodeURIComponent(params.user)}`);
  if (params.date) query.push(`date=${params.date}`);
  if (query.length) url += '?' + query.join('&');
  const res = await fetch(url, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки логов');
  return res.json();
} 