import api from '../../services/api';
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

export interface DashboardStats {
  period_days: number;
  total_bookings: number;
  completed_bookings: number;
  pending_bookings: number;
  cancelled_bookings: number;
  total_revenue: number;
  average_price: number;
  unique_clients: number;
  completion_rate: number;
}

export interface RecentBooking {
  id: number;
  client_name: string;
  date: string;
  start_time: string;
  status: string;
}

/**
 * Create a new booking via the backend API
 */
export async function createBookingApi(bookingData: CreateBookingRequest): Promise<CreateBookingResponse> {
  try {
    const response = await api.post<CreateBookingResponse>('/bookings/public/', bookingData);
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
    const response = await api.get<CreateBookingResponse>(`/bookings/${bookingId}`);
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
    const response = await api.get<CreateBookingResponse[]>('/bookings/');
    return response.data;
  } catch (error) {
    console.error('Error fetching bookings:', error);
    throw error;
  }
}

/**
 * Get bookings within a date range
 */
export async function getBookingsByDateRangeApi(startDate: string, endDate: string): Promise<CreateBookingResponse[]> {
  try {
    const response = await api.get<CreateBookingResponse[]>('/bookings/', {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching bookings from ${startDate} to ${endDate}:`, error);
    throw error;
  }
}

/**
 * Get dashboard statistics
 */
export async function getDashboardStatsApi(startDate?: string, endDate?: string): Promise<DashboardStats> {
  try {
    // Use the new public endpoint for dashboard stats
    const response = await api.get<DashboardStats>('/bookings/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
}

/**
 * Get recent bookings for dashboard
 */
export async function getRecentBookingsApi(limit: number = 10, startDate?: string, endDate?: string): Promise<RecentBooking[]> {
  try {
    // Use the new public endpoint for recent bookings
    const response = await api.get<RecentBooking[]>('/bookings/recent', {
      params: {
        limit: limit
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching recent bookings:', error);
    throw error;
  }
}