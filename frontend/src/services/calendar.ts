import axios from 'axios';

export interface CalendarEvent {
  id: string;
  summary: string;
  start: {
    dateTime: string;
  };
  end: {
    dateTime: string;
  };
  description?: string;
}

export class CalendarService {
  private static api = axios.create({
    baseURL: 'http://localhost:8000/api',
  });

  static async getEvents(startDate: Date, endDate: Date): Promise<CalendarEvent[]> {
    try {
      const response = await this.api.get('/calendar/events', {
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
        },
      });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении событий календаря:', error);
      throw error;
    }
  }

  static async getAvailability(date: Date): Promise<string[]> {
    try {
      const response = await this.api.get('/calendar/availability', {
        params: {
          date: date.toISOString(),
        },
      });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении доступных слотов:', error);
      throw error;
    }
  }
} 