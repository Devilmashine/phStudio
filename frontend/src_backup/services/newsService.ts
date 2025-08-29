export interface NewsItem {
  id: number;
  title: string;
  content: string;
  published?: number;
  created_at?: string;
  updated_at?: string;
}

const API_URL = '/news/'; // Removed /api prefix since it's already in the base URL // trailing slash для избежания 307 Redirect

export async function fetchNews(): Promise<NewsItem[]> {
  const res = await fetch(API_URL);
  if (!res.ok) throw new Error('Ошибка загрузки новостей');
  return res.json();
}

export async function createNews(data: Partial<NewsItem>, headers: Record<string, string>): Promise<NewsItem> {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Ошибка создания новости');
  return res.json();
}

export async function updateNews(id: number, data: Partial<NewsItem>, headers: Record<string, string>): Promise<NewsItem> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Ошибка обновления новости');
  return res.json();
}

export async function deleteNews(id: number, headers: Record<string, string>): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
    headers,
  });
  if (!res.ok) throw new Error('Ошибка удаления новости');
}