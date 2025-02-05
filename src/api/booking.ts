import axios from 'axios';
import { BookingFormData, BookingResponse } from '@/types/booking';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const createBooking = async (data: BookingFormData): Promise<BookingResponse> => {
  try {
    const response = await axios.post<BookingResponse>(`${API_URL}/bookings`, data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Ошибка при создании бронирования');
    }
    throw new Error('Ошибка сети');
  }
};

export const getAvailableSlots = async (date: string) => {
  try {
    const response = await axios.get(`${API_URL}/calendar/available-slots`, {
      params: { date }
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Ошибка при получении доступных слотов');
    }
    throw new Error('Ошибка сети');
  }
}; 