import api from '../api';
import { BookingData } from '../../types';

export interface CreateBookingRequest {
  date: string; // YYYY-MM-DD format
  start_time: string; // ISO format datetime in Moscow timezone
  end_time: string; // ISO format datetime in Moscow timezone
  total_price: number;
  client_name: string;
  client_phone: string;
  client_email?: string;
  notes?: string;
}

export interface CreateBookingResponse {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  total_price: number;
  client_name: string;
  client_phone: string;
  client_email?: string;
  notes?: string;
  status: string;
  created_at: string;
  updated_at: string;
  calendar_event_id?: string;
}

/**
 * Create a new booking via the backend API
 */
export async function createBookingApi(bookingData: CreateBookingRequest): Promise<CreateBookingResponse> {
  try {
    const response = await api.post<CreateBookingResponse>('/api/bookings/public/', bookingData);
    return response.data;
  } catch (error) {
    console.error('Error creating booking via API:', error);
    throw error;
  }
}

/**
 * Get booking by ID
 */
export async function getBookingApi(bookingId: number): Promise<CreateBookingResponse> {
  try {
    const response = await api.get<CreateBookingResponse>(`/api/bookings/${bookingId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching booking ${bookingId}:`, error);
    throw error;
  }
}

/**
 * Get all bookings
 */
export async function getBookingsApi(): Promise<CreateBookingResponse[]> {
  try {
    const response = await api.get<CreateBookingResponse[]>('/api/bookings/');
    return response.data;
  } catch (error) {
    console.error('Error fetching bookings:', error);
    throw error;
  }
}