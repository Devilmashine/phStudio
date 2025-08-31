import axios from 'axios';
import { BookingFormData, BookingResponse } from '../types/booking';
import { apiClient } from '../utils/api';

// Updated import paths to be relative instead of using @ alias
export const bookingApi = {
  createBooking: (data: BookingFormData) => 
    apiClient.post<BookingResponse>('/bookings/public/', data),
  
  getBookings: () => 
    apiClient.get<BookingResponse[]>('/bookings/'),
  
  getBooking: (id: number) => 
    apiClient.get<BookingResponse>(`/bookings/${id}`),
  
  updateBooking: (id: number, data: Partial<BookingFormData>) => 
    apiClient.put<BookingResponse>(`/bookings/${id}`, data),
  
  deleteBooking: (id: number) => 
    apiClient.delete(`/bookings/${id}`),
};