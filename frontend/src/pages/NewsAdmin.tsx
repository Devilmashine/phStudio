import React, { useEffect, useState } from 'react';
import { fetchNews, NewsItem, createNews, updateNews, deleteNews } from '../services/newsService';
import { useToast } from '../components/Toast';

const NewsAdmin: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<{ title: string; content: string }>({ title: '', content: '' });
  const [editId, setEditId] = useState<number | null>(null);
  const toast = useToast?.();

  const loadNews = async () => {
    setLoading(true);
    try {
      const data = await fetchNews();
      setNews(data);
    } catch {
      setError('Ошибка загрузки новостей');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNews();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (editId) {
        await updateNews(editId, form);
        toast?.show('Новость обновлена');
      } else {
        await createNews({ ...form, published: 1 });
        toast?.show('Новость опубликована');
      }
      setForm({ title: '', content: '' });
      setEditId(null);
      await loadNews();
    } catch (err) {
      console.error(err);
      setError('Ошибка сохранения новости');
      toast?.show('Ошибка сохранения');
    }
  };

  const handleEdit = (item: NewsItem) => {
    setForm({ title: item.title, content: item.content });
    setEditId(item.id);
  };

  const handleDelete = async (id: number) => {
    setError(null);
    try {
      await deleteNews(id);
      toast?.show('Новость удалена');
      await loadNews();
    } catch (err) {
      console.error(err);
      setError('Ошибка удаления новости');
      toast?.show('Ошибка удаления');
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Управление новостями</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <form onSubmit={handleSubmit} className="mb-6 flex gap-2">
        <input
          type="text"
          placeholder="Заголовок"
          value={form.title}
          onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          className="border px-2 py-1 rounded w-1/4"
          required
        />
        <input
          type="text"
          placeholder="Текст"
          value={form.content}
          onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
          className="border px-2 py-1 rounded w-1/2"
          required
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          {editId ? 'Сохранить' : 'Добавить'}
        </button>
        {editId && (
          <button type="button" onClick={() => { setEditId(null); setForm({ title: '', content: '' }); }} className="ml-2 px-4 py-2 rounded border">
            Отмена
          </button>
        )}
      </form>
      {loading ? (
        <div>Загрузка...</div>
      ) : (
        <table className="w-full border">
          <thead>
            <tr>
              <th>ID</th>
              <th>Заголовок</th>
              <th>Текст</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {news.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.title}</td>
                <td>{item.content}</td>
                <td>
                  <button className="text-blue-600 mr-2" onClick={() => handleEdit(item)}>Редактировать</button>
                  <button className="text-red-600" onClick={() => handleDelete(item.id)}>Удалить</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default NewsAdmin;
