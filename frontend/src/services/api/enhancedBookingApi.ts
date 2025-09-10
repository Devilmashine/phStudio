/**
 * Enhanced Booking API Client
 * Интеграция с новым enhanced booking backend API
 */

import api from '../api';
import {
  EnhancedBooking,
  CreateBookingRequest,
  UpdateBookingRequest,
  BookingStateTransitionRequest,
  BookingFilters,
  PaginatedResponse,
  ApiResponse
} from '../../stores/types';

interface BookingQueryParams extends BookingFilters {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

interface BookingAnalyticsResponse {
  total_bookings: number;
  completed_bookings: number;
  pending_bookings: number;
  cancelled_bookings: number;
  total_revenue: number;
  average_price: number;
  unique_clients: number;
  completion_rate: number;
  revenue_by_month: Array<{ month: string; revenue: number }>;
  bookings_by_state: Array<{ state: string; count: number }>;
  popular_time_slots: Array<{ hour: number; count: number }>;
}

class EnhancedBookingApi {
  private readonly basePath = '/v2/bookings';

  /**
   * Get paginated list of bookings with filters
   */
  async getBookings(params?: BookingQueryParams): Promise<PaginatedResponse<EnhancedBooking>> {
    const response = await api.get<PaginatedResponse<EnhancedBooking>>(this.basePath, {
      params: this.cleanParams(params),
    });
    return response.data;
  }

  /**
   * Get single booking by ID
   */
  async getBooking(id: number): Promise<EnhancedBooking> {
    const response = await api.get<ApiResponse<EnhancedBooking>>(`${this.basePath}/${id}`);
    return response.data.data;
  }

  /**
   * Create new booking
   */
  async createBooking(data: CreateBookingRequest): Promise<EnhancedBooking> {
    const response = await api.post<ApiResponse<EnhancedBooking>>(this.basePath, data);
    return response.data.data;
  }

  /**
   * Update existing booking
   */
  async updateBooking(id: number, data: UpdateBookingRequest): Promise<EnhancedBooking> {
    const response = await api.put<ApiResponse<EnhancedBooking>>(`${this.basePath}/${id}`, data);
    return response.data.data;
  }

  /**
   * Transition booking state (using CQRS command)
   */
  async transitionBookingState(id: number, data: BookingStateTransitionRequest): Promise<EnhancedBooking> {
    const response = await api.post<ApiResponse<EnhancedBooking>>(
      `${this.basePath}/${id}/state`,
      data
    );
    return response.data.data;
  }

  /**
   * Cancel booking (convenience method)
   */
  async cancelBooking(id: number, reason?: string): Promise<EnhancedBooking> {
    const response = await api.post<ApiResponse<EnhancedBooking>>(
      `${this.basePath}/${id}/cancel`,
      { reason }
    );
    return response.data.data;
  }

  /**
   * Delete booking (soft delete)
   */
  async deleteBooking(id: number): Promise<void> {
    await api.delete(`${this.basePath}/${id}`);
  }

  /**
   * Get booking analytics
   */
  async getBookingAnalytics(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<BookingAnalyticsResponse> {
    const response = await api.get<ApiResponse<BookingAnalyticsResponse>>(
      `${this.basePath}/analytics/summary`,
      { params }
    );
    return response.data.data;
  }

  /**
   * Get bookings for specific date
   */
  async getBookingsForDate(date: string): Promise<EnhancedBooking[]> {
    const response = await api.get<ApiResponse<EnhancedBooking[]>>(
      `${this.basePath}/by-date/${date}`
    );
    return response.data.data;
  }

  /**
   * Check availability for time slot
   */
  async checkAvailability(params: {
    date: string;
    start_time: string;
    end_time: string;
    space_type?: string;
  }): Promise<{ available: boolean; conflicts?: EnhancedBooking[] }> {
    const response = await api.get<ApiResponse<{ available: boolean; conflicts?: EnhancedBooking[] }>>(
      `${this.basePath}/availability`,
      { params }
    );
    return response.data.data;
  }

  /**
   * Get booking history for client
   */
  async getClientBookingHistory(clientPhone: string): Promise<EnhancedBooking[]> {
    const response = await api.get<ApiResponse<EnhancedBooking[]>>(
      `${this.basePath}/client-history`,
      { params: { client_phone: clientPhone } }
    );
    return response.data.data;
  }

  /**
   * Bulk update bookings
   */
  async bulkUpdateBookings(data: {
    booking_ids: number[];
    updates: Partial<UpdateBookingRequest>;
  }): Promise<EnhancedBooking[]> {
    const response = await api.post<ApiResponse<EnhancedBooking[]>>(
      `${this.basePath}/bulk-update`,
      data
    );
    return response.data.data;
  }

  /**
   * Export bookings to CSV
   */
  async exportBookings(params?: BookingQueryParams): Promise<Blob> {
    const response = await api.get(`${this.basePath}/export`, {
      params: this.cleanParams(params),
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Get booking statistics for dashboard
   */
  async getDashboardStats(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<{
    total_bookings: number;
    completed_bookings: number;
    pending_bookings: number;
    cancelled_bookings: number;
    total_revenue: number;
    average_price: number;
    completion_rate: number;
  }> {
    const response = await api.get<ApiResponse<any>>(
      `${this.basePath}/stats/dashboard`,
      { params }
    );
    return response.data.data;
  }

  /**
   * Get recent bookings
   */
  async getRecentBookings(limit: number = 10): Promise<EnhancedBooking[]> {
    const response = await api.get<ApiResponse<EnhancedBooking[]>>(
      `${this.basePath}/recent`,
      { params: { limit } }
    );
    return response.data.data;
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get<ApiResponse<{ status: string; timestamp: string }>>(
      `${this.basePath}/health`
    );
    return response.data.data;
  }

  /**
   * Clean undefined/null parameters
   */
  private cleanParams(params?: any): any {
    if (!params) return {};
    
    const cleaned: any = {};
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        cleaned[key] = params[key];
      }
    });
    
    return cleaned;
  }
}

// Export singleton instance
export const enhancedBookingApi = new EnhancedBookingApi();
export default enhancedBookingApi;
