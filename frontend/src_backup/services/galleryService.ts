export interface GalleryImage {
  id: number;
  filename: string;
  url: string;
  description?: string;
  uploaded_at?: string;
}

const API_URL = '/gallery/';  // Removed /api prefix since it's already in the base URL

export async function fetchGallery(): Promise<GalleryImage[]> {
  const res = await fetch(API_URL);
  if (!res.ok) throw new Error('Ошибка загрузки галереи');
  return res.json();
}

export async function uploadImage(file: File, description: string, headers: Record<string, string>): Promise<GalleryImage> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('description', description);
  const res = await fetch(API_URL + 'upload', {
    method: 'POST',
    headers,
    body: formData,
  });
  if (!res.ok) throw new Error('Ошибка загрузки изображения');
  return res.json();
}

export async function deleteImage(id: number, headers: Record<string, string>): Promise<void> {
  const res = await fetch(`${API_URL}${id}`, {
    method: 'DELETE',
    headers,
  });
  if (!res.ok) throw new Error('Ошибка удаления изображения');
}