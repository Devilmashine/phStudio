import { bookingApi } from '../utils/api';
import { BookingData } from '../utils/validation';

interface BookingResponse {
  message?: string;
  booking_id?: string;
  calendar_link?: string;
  telegram_notification?: boolean;
  details?: Record<string, any>;
}

export const createBooking = async (bookingData: Omit<BookingData, 'description' | 'id'>) => {
  try {
    console.error('📤 ОТЛАДКА createBooking', {
      bookingData: JSON.stringify(bookingData, null, 2)
    });

    const response = await bookingApi.post<BookingResponse>('/api/bookings', bookingData);
    
    if (response.message) {
      console.log('Бронирование успешно:', response);
      return {
        booking_id: response.booking_id || 'unknown',
        calendar_link: response.calendar_link || '',
        telegram_notification: response.telegram_notification || false,
        details: response.details || {}
      };
    }
    
    throw new Error('Неверный формат ответа');
  } catch (error) {
    console.error('Ошибка бронирования:', error);
    throw error;
  }
};
