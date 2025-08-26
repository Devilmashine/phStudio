import React, { useEffect, useState, useRef } from 'react';
import { fetchGallery, uploadImage, deleteImage, GalleryImage } from '../services/galleryService';
import { useToast } from './Toast';

const getAdminHeaders = () => ({
  'X-User-Role': 'admin',
  'X-User-Id': '1',
  'X-User-Name': 'admin',
});

const Gallery: React.FC = () => {
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const toast = useToast?.();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadGallery = async () => {
    setLoading(true);
    try {
      const data = await fetchGallery();
      setImages(data);
    } catch {
      setError('Ошибка загрузки галереи');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGallery();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    try {
      await uploadImage(file, description, getAdminHeaders());
      setFile(null);
      setDescription('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      toast?.show('Изображение загружено');
      await loadGallery();
    } catch {
      setError('Ошибка загрузки изображения');
      toast?.show('Ошибка загрузки изображения');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteImage(id, getAdminHeaders());
      toast?.show('Изображение удалено');
      await loadGallery();
    } catch {
      setError('Ошибка удаления');
      toast?.show('Ошибка удаления');
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Галерея</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <form onSubmit={handleUpload} className="mb-6 flex gap-2 items-center">
        <input
          type="file"
          accept="image/*"
          onChange={e => setFile(e.target.files?.[0] || null)}
          ref={fileInputRef}
          className="border px-2 py-1 rounded"
          required
        />
        <input
          type="text"
          placeholder="Описание"
          value={description}
          onChange={e => setDescription(e.target.value)}
          className="border px-2 py-1 rounded"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Загрузить</button>
      </form>
      {loading ? (
        <div>Загрузка...</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {images.map(img => (
            <div key={img.id} className="relative group border rounded overflow-hidden">
              <img src={img.url} alt={img.description || img.filename} className="w-full h-40 object-cover" />
              <div className="p-2 text-sm text-gray-700">{img.description}</div>
              <button
                className="absolute top-2 right-2 bg-red-600 text-white rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition"
                onClick={() => handleDelete(img.id)}
                title="Удалить"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export { Gallery };
