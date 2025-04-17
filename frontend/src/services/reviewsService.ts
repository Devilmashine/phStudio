export interface Review {
  id: number;
  client_name: string;
  rating: number;
  text: string;
  status: string;
}

const API_URL = '/api/admin/reviews';

export async function fetchReviews(params: { status?: string; rating?: string } = {}): Promise<Review[]> {
  let url = API_URL;
  const query = [];
  if (params.status) query.push(`status=${params.status}`);
  if (params.rating) query.push(`rating=${params.rating}`);
  if (query.length) url += '?' + query.join('&');
  const res = await fetch(url, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка загрузки отзывов');
  return res.json();
}

export async function bulkReviewAction(ids: number[], action: 'approve' | 'hide' | 'delete'): Promise<void> {
  await Promise.all(ids.map(id =>
    fetch(`${API_URL}/${id}/${action}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
  ));
}

export async function deleteReview(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Ошибка удаления отзыва');
} 