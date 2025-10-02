import React, { useEffect, useState } from 'react';
import api from '../../services/api';

interface CalendarEvent {
  id: number;
  title: string;
  start: string;
  end: string;
  status: 'pending' | 'confirmed' | 'cancelled';
}

const ClientEventsTable: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await api.get('/calendar-events');
        setEvents(data);
      } catch (err) {
        console.error(err);
        setError('Ошибка загрузки событий');
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  if (loading) return <div>Загрузка событий...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!events.length) return <div>Нет событий.</div>;

  return (
    <table className="min-w-full border mt-4">
      <thead>
        <tr>
          <th className="border px-2 py-1">Дата</th>
          <th className="border px-2 py-1">Время</th>
          <th className="border px-2 py-1">Описание</th>
          <th className="border px-2 py-1">Экспорт</th>
        </tr>
      </thead>
      <tbody>
        {events.map(event => (
          <tr key={event.id}>
            <td className="border px-2 py-1">{event.start.split('T')[0]}</td>
            <td className="border px-2 py-1">{event.start.split('T')[1]?.slice(0,5)} - {event.end.split('T')[1]?.slice(0,5)}</td>
            <td className="border px-2 py-1">{event.title}</td>
            <td className="border px-2 py-1">
              <a
                href={`/api/calendar-events/${event.id}/ical`}
                className="text-blue-600 underline"
                download
                title="Скачать .ics для этого события"
              >
                Добавить в календарь
              </a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ClientEventsTable;
