import { google } from 'googleapis';
import { GOOGLE_CALENDAR_CONFIG } from '../../config/google-calendar';

export const calendarClient = google.calendar({
  version: 'v3',
  auth: GOOGLE_CALENDAR_CONFIG.apiKey,
});