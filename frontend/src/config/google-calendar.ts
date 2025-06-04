import { CALENDAR_CONFIG } from './calendar';

export const GOOGLE_CALENDAR_CONFIG = {
  apiKey: CALENDAR_CONFIG.apiKey, // Используем apiKey из CALENDAR_CONFIG
  calendarId: CALENDAR_CONFIG.calendarId, // Используем calendarId из CALENDAR_CONFIG
  timeZone: CALENDAR_CONFIG.timeZone, // Используем timeZone из CALENDAR_CONFIG
  serviceAccountKeyPath: './src/config/phstudiocalendar-ab930ccf1a99.json', // Указываем правильный путь к файлу ключа
};