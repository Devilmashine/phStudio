import axios from 'axios';

export interface CalendarEvent {
  id?: string;
  summary?: string;
  description?: string;
  start: { dateTime?: string; date?: string };
  end: { dateTime?: string; date?: string };
  location?: string;
}

// New interfaces for bulk month availability
export interface MonthAvailabilityResponse {
  [date: string]: {
    available_slots: number;
    total_slots: number;
    booked_slots: number;
  };
}

export interface DayDetailResponse {
  date: string;
  slots: {
    time: string;
    available: boolean;
  }[];
}

function toDateString(iso: string) {
  // Оставляем только YYYY-MM-DD
  return iso.split('T')[0];
}

/**
 * Получить события календаря через собственный API
 */
export async function fetchCalendarEvents(timeMin: string, timeMax: string): Promise<CalendarEvent[]> {
  const response = await axios.get('/api/calendar-events/', {
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
  // Validate required fields
  if (!event.summary || typeof event.summary !== 'string' || !event.summary.trim()) {
    throw new Error('summary (title) обязателен и должен быть непустой строкой');
  }
  if (!event.start?.dateTime || typeof event.start.dateTime !== 'string' || !event.start.dateTime.trim()) {
    throw new Error('start_time обязателен и должен быть непустой строкой');
  }
  if (!event.end?.dateTime || typeof event.end.dateTime !== 'string' || !event.end.dateTime.trim()) {
    throw new Error('end_time обязателен и должен быть непустой строкой');
  }
  
  // Create payload matching CalendarEventCreate schema
  const payload = {
    title: event.summary,
    description: event.description || `Booking for ${event.phone}`,
    start_time: event.start.dateTime,
    end_time: event.end.dateTime,
    people_count: (event as any).people_count || (event as any).peopleCount || 1,
    status: 'pending'
  };
  
  console.log('Creating calendar event with payload:', payload);
  const response = await axios.post('/api/calendar-events/', payload);
  return response.data;
}

// NEW: Bulk request for month availability data - single API call for entire month
export async function fetchMonthAvailability(year: number, month: number): Promise<MonthAvailabilityResponse> {
  console.log(`Fetching month availability for ${year}-${month.toString().padStart(2, '0')}`);
  const response = await axios.get('/api/calendar/month-availability', {
    params: {
      year,
      month
    }
  });
  console.log(`Month availability received:`, response.data);
  return response.data;
}

// NEW: Detailed request for specific day slots - only when day is selected
export async function fetchDayDetails(date: string): Promise<DayDetailResponse> {
  console.log(`Fetching day details for ${date}`);
  const response = await axios.get('/api/calendar/day-details', {
    params: {
      date
    }
  });
  console.log(`Day details received:`, response.data);
  return response.data;
}