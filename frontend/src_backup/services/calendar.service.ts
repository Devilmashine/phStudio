import { calendar_v3, google } from 'googleapis';
import { GoogleAuth } from 'google-auth-library';
import { OAuth2Client } from 'google-auth-library';

export interface CalendarEvent {
  id?: string;
  title: string;
  summary?: string;
  start: Date;
  end: Date;
  description?: string;
}

export class CalendarService {
  private static instance: CalendarService;
  private calendarClient: calendar_v3.Calendar;
  private auth: GoogleAuth;

  private constructor() {
    const credentials = {
      client_email: process.env.VITE_GOOGLE_CLIENT_EMAIL,
      private_key: process.env.VITE_GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n')
    };

    if (!credentials.client_email || !credentials.private_key) {
      throw new Error('Google service account credentials are missing');
    }

    this.auth = new GoogleAuth({
      credentials: {
        client_email: credentials.client_email,
        private_key: credentials.private_key
      },
      scopes: ['https://www.googleapis.com/auth/calendar']
    });

    this.calendarClient = google.calendar('v3');
  }

  public static getInstance(): CalendarService {
    if (!CalendarService.instance) {
      CalendarService.instance = new CalendarService();
    }
    return CalendarService.instance;
  }

  private getCalendarId(): string {
    return process.env.VITE_GOOGLE_CALENDAR_ID || 'primary';
  }

  private async getAuthorizedClient(): Promise<OAuth2Client> {
    try {
      const client = await this.auth.getClient();
      return client as OAuth2Client;
    } catch (error) {
      console.error('Failed to get authorized client', error);
      throw error;
    }
  }

  public async addEvent(eventData: CalendarEvent): Promise<calendar_v3.Schema$Event> {
    try {
      const authClient = await this.getAuthorizedClient();
      
      const response = await this.calendarClient.events.insert({
        auth: authClient,
        calendarId: this.getCalendarId(),
        requestBody: {
          summary: eventData.title,
          description: eventData.description,
          start: {
            dateTime: eventData.start.toISOString(),
            timeZone: 'Europe/Moscow'
          },
          end: {
            dateTime: eventData.end.toISOString(),
            timeZone: 'Europe/Moscow'
          }
        }
      });

      return response?.data || {};
    } catch (error) {
      console.error('Error adding event', error);
      throw error;
    }
  }

  public async updateEvent(
    eventId: string, 
    eventData: Partial<calendar_v3.Schema$Event>
  ): Promise<calendar_v3.Schema$Event> {
    try {
      const authClient = await this.getAuthorizedClient();
      
      const response = await this.calendarClient.events.update({
        auth: authClient,
        calendarId: this.getCalendarId(),
        eventId: eventId,
        requestBody: eventData
      });

      return response?.data || {};
    } catch (error) {
      console.error('Error updating event', error);
      throw error;
    }
  }

  public async deleteEvent(eventId: string): Promise<void> {
    try {
      const authClient = await this.getAuthorizedClient();
      
      await this.calendarClient.events.delete({
        auth: authClient,
        calendarId: this.getCalendarId(),
        eventId: eventId
      });
    } catch (error) {
      console.error('Error deleting event', error);
      throw error;
    }
  }

  public async createEvent(eventData: {
    summary: string;
    description?: string;
    start: {
      dateTime: string;
      timeZone: string;
    };
    end: {
      dateTime: string;
      timeZone: string;
    };
    colorId?: string;
    status?: string;
  }): Promise<calendar_v3.Schema$Event> {
    try {
      const authClient = await this.getAuthorizedClient();
      
      const response = await this.calendarClient.events.insert({
        auth: authClient,
        calendarId: this.getCalendarId(),
        requestBody: {
          ...eventData,
          reminders: {
            useDefault: false,
            overrides: []
          }
        }
      });

      return response?.data || {};
    } catch (error) {
      console.error('Error creating event', error);
      throw error;
    }
  }
}

export const calendarService = CalendarService.getInstance();