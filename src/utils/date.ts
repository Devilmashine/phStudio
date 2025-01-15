import { format } from 'date-fns';
import { CALENDAR_CONFIG } from '../config/calendar';

export function formatDateForCalendar(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, "yyyy-MM-dd'T'HH:mm:ssxxx");
}

export function getTimeRange(date: string) {
  return {
    timeMin: `${date}T${String(CALENDAR_CONFIG.workingHours.start).padStart(2, '0')}:00:00+03:00`,
    timeMax: `${date}T${String(CALENDAR_CONFIG.workingHours.end).padStart(2, '0')}:00:00+03:00`
  };
}