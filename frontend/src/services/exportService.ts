export type ExportType = 'bookings' | 'reviews';
export type ExportFormat = 'pdf' | 'excel';

const API_URL = '/api/admin/export';

export async function exportData(type: ExportType, format: ExportFormat): Promise<Blob> {
  const res = await fetch(`${API_URL}?type=${type}&format=${format}`, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка экспорта данных');
  return res.blob();
} 