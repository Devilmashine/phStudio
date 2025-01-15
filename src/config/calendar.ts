/**
 * Calendar configuration
 * These values should be set in environment variables
 */
export const CALENDAR_CONFIG = {
  calendarId: import.meta.env.VITE_GOOGLE_CALENDAR_ID || '',
  apiKey: import.meta.env.VITE_GOOGLE_CALENDAR_API_KEY || '',
  timeZone: 'Europe/Moscow',
  workingHours: {
    start: 9,  // 9:00 AM
    end: 20,   // 8:00 PM
  },
} as const;

// Validate required environment variables
if (!CALENDAR_CONFIG.calendarId) {
  throw new Error('VITE_GOOGLE_CALENDAR_ID environment variable is not set');
}

if (!CALENDAR_CONFIG.apiKey) {
  throw new Error('VITE_GOOGLE_CALENDAR_API_KEY environment variable is not set');
}

export type CalendarConfig = typeof CALENDAR_CONFIG;