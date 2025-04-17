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
  const response = await axios.get('/api/calendar/events', {
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
export async function createCalendarEvent(event: CalendarEvent): Promise<CalendarEvent> {
  // Преобразуем в формат, который ожидает бэкенд
  const payload = {
    title: event.summary || '',
    description: event.description || '',
    start_time: event.start?.dateTime || event.start?.date || '',
    duration_hours: event.end && event.start && event.end.dateTime && event.start.dateTime
      ? Math.max(1, Math.round((new Date(event.end.dateTime).getTime() - new Date(event.start.dateTime).getTime()) / (1000 * 60 * 60)))
      : 1
  };
  const response = await axios.post('/api/calendar/events', payload);
  return response.data;
}