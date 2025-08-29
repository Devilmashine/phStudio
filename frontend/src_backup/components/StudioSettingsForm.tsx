import React, { useEffect, useState } from 'react';
import { fetchSettings, updateSettings, StudioSettings } from '../services/settingsService';
import { useToast } from './Toast';

const StudioSettingsForm: React.FC = () => {
  const [settings, setSettings] = useState<StudioSettings | null>(null);
  const [form, setForm] = useState<Partial<StudioSettings>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast?.();

  useEffect(() => {
    fetchSettings()
      .then(data => {
        setSettings(data);
        setForm(data);
      })
      .catch(() => setError('Ошибка загрузки настроек'))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await updateSettings(form);
      setSettings(updated);
      toast?.show('Настройки сохранены');
    } catch {
      setError('Ошибка сохранения');
      toast?.show('Ошибка сохранения');
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!settings) return <div>Нет данных</div>;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Настройки студии</h2>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-xl">
        <div>
          <label className="block mb-1 font-medium">Название</label>
          <input name="name" value={form.name || ''} onChange={handleChange} className="border px-2 py-1 rounded w-full" required />
        </div>
        <div>
          <label className="block mb-1 font-medium">Адрес</label>
          <input name="address" value={form.address || ''} onChange={handleChange} className="border px-2 py-1 rounded w-full" required />
        </div>
        <div>
          <label className="block mb-1 font-medium">Телефон</label>
          <input name="phone" value={form.phone || ''} onChange={handleChange} className="border px-2 py-1 rounded w-full" required />
        </div>
        <div>
          <label className="block mb-1 font-medium">Email</label>
          <input name="email" value={form.email || ''} onChange={handleChange} className="border px-2 py-1 rounded w-full" required />
        </div>
        <div>
          <label className="block mb-1 font-medium">Часы работы</label>
          <input name="work_hours" value={form.work_hours || ''} onChange={handleChange} className="border px-2 py-1 rounded w-full" required />
        </div>
        <div>
          <label className="block mb-1 font-medium">Описание</label>
          <textarea name="description" value={form.description || ''} onChange={handleChange} className="border px-2 py-1 rounded w-full" rows={3} />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Сохранить</button>
      </form>
    </div>
  );
};

export { StudioSettingsForm };
