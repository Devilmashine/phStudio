export const GOOGLE_CALENDAR_CONFIG = {
  calendarId: import.meta.env.VITE_GOOGLE_CALENDAR_ID,
  apiKey: import.meta.env.VITE_GOOGLE_API_KEY,
  clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
  serviceAccountKeyPath: import.meta.env.VITE_GOOGLE_SERVICE_ACCOUNT_KEY_PATH,
  timeZone: 'Europe/Moscow', // Укажите ваш часовой пояс
};