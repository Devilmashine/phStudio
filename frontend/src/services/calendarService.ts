import { useApi } from '../hooks/useApi';

export interface CalendarEvent {
  id: string;
  summary: string;
  description: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };
  status: string;
}

export const useCalendarService = () => {
  const api = useApi<CalendarEvent>();

  const getEvents = async (startDate: string, endDate: string) => {
    return api.fetchData(`/calendar/events?start=${startDate}&end=${endDate}`);
  };

  const createEvent = async (event: Omit<CalendarEvent, 'id'>) => {
    return api.fetchData('/calendar/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  };

  const updateEvent = async (eventId: string, event: Partial<CalendarEvent>) => {
    return api.fetchData(`/calendar/events/${eventId}`, {
      method: 'PUT',
      body: JSON.stringify(event),
    });
  };

  const deleteEvent = async (eventId: string) => {
    return api.fetchData(`/calendar/events/${eventId}`, {
      method: 'DELETE',
    });
  };

  return {
    ...api,
    getEvents,
    createEvent,
    updateEvent,
    deleteEvent,
  };
}; 