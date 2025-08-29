import React, { useEffect, useState } from 'react';
import axios from 'axios';

const CalendarLinks: React.FC = () => {
  const [icalToken, setIcalToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Получить userId и ical_token из профиля пользователя (например, из localStorage или API)
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setUserId(user.id || null);
    setIcalToken(user.ical_token || null);
  }, []);

  const handleResetToken = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`/api/calendar-events/ical-token/reset/${userId}`);
      setIcalToken(res.data.ical_token);
      // Обновить localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      user.ical_token = res.data.ical_token;
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
