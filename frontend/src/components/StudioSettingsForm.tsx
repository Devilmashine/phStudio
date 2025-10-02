import React, { useEffect, useState } from 'react';
import {
  fetchSettings,
  updateSettings,
  createSettings,
  StudioSettings,
  StudioSettingsPayload,
} from '../services/settingsService';
import { useToast } from './Toast';

const dayOptions: Array<{ value: string; label: string }> = [
  { value: 'mon', label: 'Понедельник' },
  { value: 'tue', label: 'Вторник' },
  { value: 'wed', label: 'Среда' },
  { value: 'thu', label: 'Четверг' },
  { value: 'fri', label: 'Пятница' },
  { value: 'sat', label: 'Суббота' },
  { value: 'sun', label: 'Воскресенье' },
];

const defaultSettings: StudioSettingsPayload = {
  name: '',
  contacts: '',
  prices: '',
  work_days: ['mon', 'tue', 'wed', 'thu', 'fri'],
  work_start_time: '09:00',
  work_end_time: '20:00',
  base_price_per_hour: 1000,
  weekend_price_multiplier: 1.5,
  telegram_notifications_enabled: true,
  email_notifications_enabled: true,
  holidays: [],
  min_booking_duration: 1,
  max_booking_duration: 8,
  advance_booking_days: 30,
};

const StudioSettingsForm: React.FC = () => {
  const [settings, setSettings] = useState<StudioSettings | null>(null);
  const [form, setForm] = useState<StudioSettingsPayload>(defaultSettings);
  const [holidaysText, setHolidaysText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const toast = useToast?.();

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSettings();
        if (data) {
          setSettings(data);
          setForm({
            name: data.name,
            contacts: data.contacts,
            prices: data.prices,
            work_days: data.work_days,
            work_start_time: data.work_start_time,
            work_end_time: data.work_end_time,
            base_price_per_hour: data.base_price_per_hour,
            weekend_price_multiplier: data.weekend_price_multiplier,
            telegram_notifications_enabled: data.telegram_notifications_enabled,
            email_notifications_enabled: data.email_notifications_enabled,
            holidays: data.holidays ?? [],
            min_booking_duration: data.min_booking_duration,
            max_booking_duration: data.max_booking_duration,
            advance_booking_days: data.advance_booking_days,
          });
          setHolidaysText((data.holidays ?? []).join('\n'));
          setIsCreating(false);
        } else {
          setSettings(null);
          setForm(defaultSettings);
          setHolidaysText('');
          setIsCreating(true);
        }
      } catch {
        setError('Не удалось загрузить настройки студии');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const updateForm = (patch: Partial<StudioSettingsPayload>) => {
    setForm(prev => ({ ...prev, ...patch }));
    if (error) setError(null);
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    updateForm({ [name]: value } as Partial<StudioSettingsPayload>);
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const numericValue = Number(value);
    updateForm({ [name]: Number.isFinite(numericValue) ? numericValue : 0 } as Partial<StudioSettingsPayload>);
  };

  const toggleWorkDay = (day: string) => {
    setForm(prev => {
      const current = prev.work_days.includes(day)
        ? prev.work_days.filter(d => d !== day)
        : [...prev.work_days, day];

      const normalized = current.length > 0 ? current : [day];
      const ordered = dayOptions
        .map(option => option.value)
        .filter(value => normalized.includes(value));

      return { ...prev, work_days: ordered };
    });
    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const cleanedHolidays = holidaysText
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);

      const payload: StudioSettingsPayload = {
        ...form,
        base_price_per_hour: Number(form.base_price_per_hour) || 0,
        weekend_price_multiplier: Number(form.weekend_price_multiplier) || 1,
        min_booking_duration: Number(form.min_booking_duration) || 1,
        max_booking_duration: Number(form.max_booking_duration) || 8,
        advance_booking_days: Number(form.advance_booking_days) || 30,
        holidays: cleanedHolidays,
      };

      const result = isCreating
        ? await createSettings(payload)
        : await updateSettings(payload);

      setSettings(result);
      setForm({
        name: result.name,
        contacts: result.contacts,
        prices: result.prices,
        work_days: result.work_days,
        work_start_time: result.work_start_time,
        work_end_time: result.work_end_time,
        base_price_per_hour: result.base_price_per_hour,
        weekend_price_multiplier: result.weekend_price_multiplier,
        telegram_notifications_enabled: result.telegram_notifications_enabled,
        email_notifications_enabled: result.email_notifications_enabled,
        holidays: result.holidays ?? [],
        min_booking_duration: result.min_booking_duration,
        max_booking_duration: result.max_booking_duration,
        advance_booking_days: result.advance_booking_days,
      });
      setHolidaysText((result.holidays ?? []).join('\n'));
      setIsCreating(false);
      toast?.show('Настройки студии сохранены');
    } catch (err) {
      console.error(err);
      setError('Ошибка сохранения настроек');
      toast?.show('Ошибка сохранения настроек');
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  const isNewConfig = !settings && isCreating;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Настройки студии</h2>
          <p className="text-sm text-gray-500">
            Определите режим работы, цены и уведомления для CRM.
          </p>
        </div>
        {isNewConfig && (
          <span className="text-sm text-gray-500">Создайте запись с ключевыми параметрами студии</span>
        )}
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <section className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Название студии</label>
            <input
              name="name"
              value={form.name}
              onChange={handleTextChange}
              className="border px-3 py-2 rounded w-full"
              required
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Контактная информация</label>
            <textarea
              name="contacts"
              value={form.contacts}
              onChange={handleTextChange}
              className="border px-3 py-2 rounded w-full"
              rows={4}
              placeholder="Телефон, email, адрес"
              required
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Информация о ценах</label>
            <textarea
              name="prices"
              value={form.prices}
              onChange={handleTextChange}
              className="border px-3 py-2 rounded w-full"
              rows={4}
              placeholder="Опишите тарифы и пакеты"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block mb-1 font-medium">Базовая цена, ₽/час</label>
              <input
                name="base_price_per_hour"
                type="number"
                min={0}
                step={100}
                value={form.base_price_per_hour}
                onChange={handleNumberChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Множитель в выходные</label>
              <input
                name="weekend_price_multiplier"
                type="number"
                min={1}
                step={0.1}
                value={form.weekend_price_multiplier}
                onChange={handleNumberChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Рабочие дни</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {dayOptions.map(day => (
                <label key={day.value} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={form.work_days.includes(day.value)}
                    onChange={() => toggleWorkDay(day.value)}
                  />
                  <span>{day.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block mb-1 font-medium">Начало рабочего дня</label>
              <input
                type="time"
                name="work_start_time"
                value={form.work_start_time}
                onChange={handleTextChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Конец рабочего дня</label>
              <input
                type="time"
                name="work_end_time"
                value={form.work_end_time}
                onChange={handleTextChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block mb-1 font-medium">Мин. длительность, ч</label>
              <input
                type="number"
                name="min_booking_duration"
                min={1}
                max={form.max_booking_duration}
                value={form.min_booking_duration}
                onChange={handleNumberChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Макс. длительность, ч</label>
              <input
                type="number"
                name="max_booking_duration"
                min={form.min_booking_duration}
                value={form.max_booking_duration}
                onChange={handleNumberChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Дней вперёд</label>
              <input
                type="number"
                name="advance_booking_days"
                min={1}
                value={form.advance_booking_days}
                onChange={handleNumberChange}
                className="border px-3 py-2 rounded w-full"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block mb-1 font-medium">Праздничные дни (по одному в строке, формат YYYY-MM-DD)</label>
            <textarea
              value={holidaysText}
              onChange={e => setHolidaysText(e.target.value)}
              className="border px-3 py-2 rounded w-full"
              rows={4}
              placeholder="2025-01-01\n2025-05-09"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <label className="flex items-center gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={form.telegram_notifications_enabled}
                onChange={e => updateForm({ telegram_notifications_enabled: e.target.checked })}
              />
              Телеграм-уведомления
            </label>
            <label className="flex items-center gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={form.email_notifications_enabled}
                onChange={e => updateForm({ email_notifications_enabled: e.target.checked })}
              />
              Email-уведомления
            </label>
          </div>
        </section>

        <div className="xl:col-span-2 flex items-center gap-3">
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
            {isNewConfig ? 'Создать' : 'Сохранить'}
          </button>
          {!isNewConfig && settings && (
            <span className="text-xs text-gray-500">
              Последнее обновление: {new Date(settings.updated_at ?? settings.created_at).toLocaleString('ru-RU')}
            </span>
          )}
        </div>
      </form>
    </div>
  );
};

export { StudioSettingsForm };
