/**
 * Calendar configuration
 * Только параметры, которые можно хранить на фронте
 */
export const CALENDAR_CONFIG = {
  timeZone: 'Europe/Moscow',
  workingHours: {
    start: 9,  // 9:00 AM
    end: 20,   // 8:00 PM
  },
} as const;

export type CalendarConfig = typeof CALENDAR_CONFIG;