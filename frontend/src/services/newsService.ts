import api from './api';

export interface NewsItem {
  id: number;
  title: string;
  content: string;
  published?: number;
  created_at?: string;
  updated_at?: string;
}

const basePath = '/news';

export async function fetchNews(): Promise<NewsItem[]> {
  const { data } = await api.get<NewsItem[]>(`${basePath}/`);
  return data;
}

export async function createNews(payload: Partial<NewsItem>): Promise<NewsItem> {
  const { data } = await api.post<NewsItem>(`${basePath}/`, payload);
  return data;
}

export async function updateNews(id: number, payload: Partial<NewsItem>): Promise<NewsItem> {
  const { data } = await api.put<NewsItem>(`${basePath}/${id}`, payload);
  return data;
}

export async function deleteNews(id: number): Promise<void> {
  await api.delete(`${basePath}/${id}`);
}