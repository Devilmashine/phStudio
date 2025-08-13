import { bookingApi } from '../utils/api'; // Предполагаем, что этот импорт корректен
import { BookingData } from '../utils/validation';
import axios from 'axios';

interface BookingResponse {
  id: number;
  // ... другие поля ответа
}

export const createBooking = async (bookingData: Omit<BookingData, 'description' | 'id'>): Promise<BookingResponse> => {
  try {
    // Используем новый публичный эндпоинт
    const response = await bookingApi.post<BookingResponse>('/bookings/public/', bookingData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Если есть специфичное сообщение об ошибке от бэкенда, используем его
      if (error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      // Иначе, возвращаем общую ошибку HTTP
      throw new Error(`Ошибка сервера: ${error.response.status} ${error.response.statusText}`);
    }
    // Для непредвиденных ошибок
    throw new Error('Произошла непредвиденная ошибка при создании бронирования.');
  }
};
