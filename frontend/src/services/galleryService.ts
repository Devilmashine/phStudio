import api from './api';

export interface GalleryImage {
  id: number;
  filename: string;
  url: string;
  description?: string;
  uploaded_at?: string;
}

const basePath = '/gallery';

export async function fetchGallery(): Promise<GalleryImage[]> {
  const { data } = await api.get<GalleryImage[]>(`${basePath}/`);
  return data;
}

export async function uploadImage(file: File, description: string): Promise<GalleryImage> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('description', description);

  const { data } = await api.post<GalleryImage>(`${basePath}/upload`, formData);
  return data;
}

export async function deleteImage(id: number): Promise<void> {
  await api.delete(`${basePath}/${id}`);
}