export interface Booking {
  id: number;
  date: string;
  time: string;
  client_name: string;
  status: string;
}

const API_URL = '/api/admin/bookings';

export async function fetchBookings(params: { status?: string; date?: string } = {}): Promise<Booking[]> {
  let url = API_URL;
  const query = [];
  if (params.status) query.push(`status=${params.status}`);
  if (params.date) query.push(`date=${params.date}`);
  if (query.length) url += '?' + query.join('&');
  const res = await fetch(url, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки бронирований');
  return res.json();
}

export async function bulkAction(ids: number[], action: 'confirm' | 'cancel' | 'delete'): Promise<void> {
  await Promise.all(ids.map(id =>
    fetch(`${API_URL}/${id}/${action}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
  ));
}

export async function deleteBooking(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка удаления бронирования');
} 