import axios from 'axios';

export interface CalendarEvent {
  id?: string;
  summary?: string;
  description?: string;
  start: { dateTime?: string; date?: string };
  end: { dateTime?: string; date?: string };
  location?: string;
}

function toDateString(iso: string) {
  // Оставляем только YYYY-MM-DD
  return iso.split('T')[0];
}

/**
 * Получить события календаря через собственный API
 */
export async function fetchCalendarEvents(timeMin: string, timeMax: string): Promise<CalendarEvent[]> {
  const response = await axios.get('/api/calendar-events', {
    params: {
      start_date: toDateString(timeMin),
      end_date: toDateString(timeMax)
    }
  });
  return response.data;
}

/**
 * Создать новое событие календаря через собственный API
 * event: CalendarEvent (summary, description, start, end)
 */
export async function createCalendarEvent(event: CalendarEvent & { phone: string; total_price: number }): Promise<CalendarEvent> {
  // Преобразуем в формат, который ожидает бэкенд
  const duration = event.end && event.start && event.end.dateTime && event.start.dateTime
    ? Math.max(1, Math.round((new Date(event.end.dateTime).getTime() - new Date(event.start.dateTime).getTime()) / (1000 * 60 * 60)))
    : 1;
  if (!event.summary || typeof event.summary !== 'string' || !event.summary.trim()) {
    throw new Error('summary (title) обязателен и должен быть непустой строкой');
  }
  if (!event.start?.dateTime || typeof event.start.dateTime !== 'string' || !event.start.dateTime.trim()) {
    throw new Error('start_time обязателен и должен быть непустой строкой');
  }
  if (!event.end?.dateTime || typeof event.end.dateTime !== 'string' || !event.end.dateTime.trim()) {
    throw new Error('end_time обязателен и должен быть непустой строкой');
  }
  if (!event.phone || typeof event.phone !== 'string' || !event.phone.trim()) {
    throw new Error('Телефон обязателен и должен быть непустой строкой');
  }
  if (!event.total_price || typeof event.total_price !== 'number' || event.total_price <= 0) {
    throw new Error('total_price обязателен и должен быть положительным числом');
  }
  const payload = {
    title: event.summary || '',
    description: event.description || '',
    start_time: event.start?.dateTime || event.start?.date || '',
    end_time: event.end?.dateTime || event.end?.date || '',
    duration_hours: Number(duration),
    phone: event.phone,
    total_price: event.total_price,
    people_count: (event as any).people_count || (event as any).peopleCount || 1,
    times: [
      event.start?.dateTime ? new Date(event.start.dateTime).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : '',
      event.end?.dateTime ? new Date(event.end.dateTime).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : ''
    ]
  };
  const response = await axios.post('/api/calendar/events', payload);
  return response.data;
}