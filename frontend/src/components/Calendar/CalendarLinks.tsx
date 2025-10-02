import React, { useEffect, useState } from 'react';
import api from '../../services/api';

const CalendarLinks: React.FC = () => {
  const [icalToken, setIcalToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      const stored = sessionStorage.getItem('user') ?? localStorage.getItem('user');
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed?.id) {
            setUserId(parsed.id);
            setIcalToken(parsed.ical_token || null);
            return;
          }
        } catch {
          // ignore JSON errors and fallback to API
        }
      }

      try {
        const { data } = await api.get('/auth/users/me');
        setUserId(data.id);
        setIcalToken(data.ical_token || null);
        sessionStorage.setItem('user', JSON.stringify(data));
        localStorage.setItem('user', JSON.stringify(data));
      } catch (err) {
        console.error(err);
        setError('Не удалось загрузить профиль пользователя');
      }
    };

    loadProfile();
  }, []);

  const handleResetToken = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post(`/calendar-events/ical-token/reset/${userId}`);
      setIcalToken(data.ical_token);
      const stored = sessionStorage.getItem('user') ?? localStorage.getItem('user') ?? '{}';
      const user = JSON.parse(stored);
      user.ical_token = data.ical_token;
      sessionStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('user', JSON.stringify(user));
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Ошибка при сбросе токена');
    } finally {
      setLoading(false);
    }
  };

  if (!userId) return <div>Пользователь не найден</div>;

  const icalUrl = icalToken
    ? `${window.location.origin}/api/calendar-events/ical/${userId}/${icalToken}`
    : '';

  return (
    <div className="bg-white rounded shadow p-4 mb-4">
      <h2 className="text-lg font-bold mb-2">Экспорт календаря (iCal/Webcal)</h2>
      {icalToken ? (
        <>
          <div className="mb-2">
            <span className="font-semibold">Ваша ссылка:</span>
            <input
              type="text"
              value={icalUrl}
              readOnly
              className="w-full border px-2 py-1 rounded mt-1 text-xs"
              onFocus={e => e.target.select()}
            />
          </div>
          <div className="flex gap-2 mb-2">
            <button
              className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
              onClick={() => navigator.clipboard.writeText(icalUrl)}
            >
              Копировать ссылку
            </button>
            <button
              className="bg-gray-200 text-gray-800 px-3 py-1 rounded hover:bg-gray-300"
              onClick={handleResetToken}
              disabled={loading}
            >
              Сбросить токен
            </button>
          </div>
          <div className="text-xs text-gray-500">
            Добавьте ссылку в Google Calendar, Apple Calendar или другое приложение.<br />
            Для Webcal используйте <b>webcal://</b> вместо <b>https://</b>.
          </div>
        </>
      ) : (
        <div>Токен не найден. Попробуйте сбросить токен.</div>
      )}
      {error && <div className="text-red-500 mt-2">{error}</div>}
    </div>
  );
};

export default CalendarLinks;
