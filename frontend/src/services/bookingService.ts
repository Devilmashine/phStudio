import { BookingResponse, BookingCreate, BookingState } from '../types/booking';

const API_BASE_URL = '/api/v2';

export class BookingService {
  static async createBooking(bookingData: BookingCreate): Promise<BookingResponse> {
    const response = await fetch(`${API_BASE_URL}/bookings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookingData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create booking: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getBookings(
    date?: string,
    state?: BookingState,
    skip: number = 0,
    limit: number = 100
  ): Promise<{ bookings: BookingResponse[]; total: number }> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    
    if (date) params.append('date', date);
    if (state) params.append('state', state);
    
    const response = await fetch(`${API_BASE_URL}/bookings?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch bookings: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getBooking(bookingId: number): Promise<BookingResponse> {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Booking not found');
      }
      throw new Error(`Failed to fetch booking: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async updateBookingState(
    bookingId: number,
    newState: BookingState,
    notes?: string
  ): Promise<BookingResponse> {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/state`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ new_state: newState, notes }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update booking state: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async deleteBooking(bookingId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete booking: ${response.statusText}`);
    }
  }
}