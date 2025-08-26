import axios from 'axios';
import { BookingFormData, BookingResponse } from '../types/booking';
import { apiClient } from './api';

// Updated import paths to be relative instead of using @ alias
export const bookingApi = {
  createBooking: (data: BookingFormData) => 
    apiClient.post<BookingResponse>('/api/bookings/bookings/public/', data),
  
  getBookings: () => 
    apiClient.get<BookingResponse[]>('/api/bookings/bookings/'),
  
  getBooking: (id: number) => 
    apiClient.get<BookingResponse>(`/api/bookings/bookings/${id}`),
  
  updateBooking: (id: number, data: Partial<BookingFormData>) => 
    apiClient.put<BookingResponse>(`/api/bookings/bookings/${id}`, data),
  
  deleteBooking: (id: number) => 
    apiClient.delete(`/api/bookings/bookings/${id}`),
};