import React, { useEffect, useState } from 'react';
import axios from 'axios';
import LoadingSpinner from '../common/LoadingSpinner';

interface CalendarEvent {
  id: number;
  title: string;
  start: string;
  end: string;
  status: 'pending' | 'confirmed' | 'cancelled';
  user_name?: string;
}

const statusMap: Record<CalendarEvent['status'], { label: string; color: string }> = {
  pending: { label: 'В ожидании', color: 'bg-yellow-100 text-yellow-800' },
  confirmed: { label: 'Подтверждено', color: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Отменено', color: 'bg-red-100 text-red-800' },
};

const CalendarEventsTable: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'pending' | 'confirmed' | 'cancelled'>('all');
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = async (statusFilter: typeof filter = filter) => {
    setLoading(true);
    setError(null);
    try {
      let url = '/api/calendar-events';
      if (statusFilter !== 'all') {
        url += `?status=${statusFilter}`;
      }
      const res = await axios.get(url);
      setEvents(res.data);
    } catch (e: any) {
      setError('Ошибка загрузки событий');
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    fetchEvents(filter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const handleAction = async (id: number, action: 'confirm' | 'cancel' | 'delete') => {
    setLoading(true);
    setError(null);
    try {
      if (action === 'delete') {
        await axios.delete(`/api/calendar-events/${id}`);
      } else {
        await axios.patch(`/api/calendar-events/${id}`, { status: action === 'confirm' ? 'confirmed' : 'cancelled' });
      }
      fetchEvents();
    } catch (e: any) {
      setError('Ошибка при выполнении действия');
    } finally {
      setLoading(false);
    }
  };

  const handleExportICS = (id: number) => {
    window.open(`/api/calendar-events/ics/${id}`, '_blank');
  };

  // Фильтрация теперь на backend, на фронте просто отображаем events
  const filteredEvents = events;

  return (
    <div className="w-full mt-8">
      <div className="flex items-center gap-4 mb-4">
        <label htmlFor="status-filter" className="font-semibold">Фильтр:</label>
        <select
          id="status-filter"
          value={filter}
          onChange={e => setFilter(e.target.value as any)}
          className="border rounded px-2 py-1 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          aria-label="Фильтр по статусу"
        >
          <option value="all">Все</option>
          <option value="pending">В ожидании</option>
          <option value="confirmed">Подтверждено</option>
          <option value="cancelled">Отменено</option>
        </select>
      </div>
      {error && <div className="text-red-500 mb-2" role="alert" aria-live="assertive">{error}</div>}
      <div className="overflow-x-auto rounded-lg shadow-sm" role="region" aria-live="polite">
        <table className="min-w-full divide-y divide-gray-200" aria-label="Таблица событий" role="table">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Время</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Название</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-400">
                  <LoadingSpinner size={8} color="indigo-600" />
                  <span className="sr-only">Загрузка...</span>
                </td>
              </tr>
            ) : filteredEvents.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Нет событий</td></tr>
            ) : (
              filteredEvents.map(ev => (
                <tr key={ev.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap" title={ev.start}>{ev.start.split('T')[0]}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{ev.start.split('T')[1]?.slice(0,5)} - {ev.end.split('T')[1]?.slice(0,5)}</td>
                  <td className="px-4 py-3 whitespace-nowrap" title={ev.title}>{ev.title}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs font-semibold border ${statusMap[ev.status].color} border-opacity-40`} tabIndex={0} aria-label={`Статус: ${statusMap[ev.status].label}`}>{statusMap[ev.status].label}</span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap flex gap-2">
                    {ev.status !== 'confirmed' && (
                      <button className="text-green-600 hover:underline focus:outline-none focus:ring-2 focus:ring-green-400 rounded px-2 py-1" onClick={() => handleAction(ev.id, 'confirm')} aria-label="Подтвердить событие">Подтвердить</button>
                    )}
                    {ev.status !== 'cancelled' && (
                      <button className="text-yellow-600 hover:underline focus:outline-none focus:ring-2 focus:ring-yellow-400 rounded px-2 py-1" onClick={() => handleAction(ev.id, 'cancel')} aria-label="Отменить событие">Отменить</button>
                    )}
                    <button className="text-red-600 hover:underline focus:outline-none focus:ring-2 focus:ring-red-400 rounded px-2 py-1" onClick={() => handleAction(ev.id, 'delete')} aria-label="Удалить событие">Удалить</button>
                    <button className="text-blue-600 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-400 rounded px-2 py-1" onClick={() => handleExportICS(ev.id)} aria-label="Добавить в календарь">Добавить в календарь</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CalendarEventsTable;
