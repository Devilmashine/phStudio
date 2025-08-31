import { bookingApi } from '../utils/api'; // Предполагаем, что этот импорт корректен
import { BookingData } from '../types/index';
import { formatLocalDate } from '../utils/dateUtils';
import axios from 'axios';

interface BookingResponse {
  id: number;
  // ... другие поля ответа
}

export const createBooking = async (bookingData: Omit<BookingData, 'description' | 'id'>): Promise<BookingResponse> => {
  try {
    // Преобразуем данные в формат, ожидаемый бэкендом (московское время)
    const dateStr = formatLocalDate(bookingData.date);
    
    // Получаем первое и последнее время из списка
    const times = bookingData.times || [];
    const startTimeStr = times.length > 0 ? times[0] : '10:00';
    const lastTimeStr = times.length > 0 ? times[times.length - 1] : '10:00';
    
    // Создаем даты в московском времени без конвертации в UTC
    const startHour = parseInt(startTimeStr.split(':')[0]);
    const startMinute = parseInt(startTimeStr.split(':')[1] || '0');
    const lastHour = parseInt(lastTimeStr.split(':')[0]);
    const lastMinute = parseInt(lastTimeStr.split(':')[1] || '0');
    
    // Форматируем даты в московском времени (UTC+3)
    const startDateTime = `${dateStr}T${startTimeStr.padStart(5, '0')}:00+03:00`;
    const endDateTime = `${dateStr}T${(lastHour + 1).toString().padStart(2, '0')}:${lastMinute.toString().padStart(2, '0')}:00+03:00`;
    
    const apiPayload = {
      date: startDateTime,
      start_time: startDateTime,
      end_time: endDateTime,
      client_name: bookingData.name,
      client_phone: bookingData.phone,
      total_price: bookingData.totalPrice,
      people_count: bookingData.peopleCount || 1
    };

    console.log('Sending API payload:', apiPayload);
    
    // Используем правильный публичный эндпоинт
    const response = await bookingApi.post<BookingResponse>('/bookings/public/', apiPayload);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Если есть специфичное сообщение об ошибке от бэкенда, используем его
      if (error.response.data && error.response.data.detail) {
        // Обрабатываем массив ошибок валидации
        if (Array.isArray(error.response.data.detail)) {
          const validationErrors = error.response.data.detail.map((err: any) => 
            `${err.loc.join('.')}: ${err.msg}`).join('; ');
          throw new Error(`Ошибка валидации: ${validationErrors}`);
        } else {
          throw new Error(error.response.data.detail);
        }
      }
      // Иначе, возвращаем общую ошибку HTTP
      throw new Error(`Ошибка сервера: ${error.response.status} ${error.response.statusText}`);
    }
    // Для непредвиденных ошибок
    throw new Error('Произошла непредвиденная ошибка при создании бронирования.');
  }
};