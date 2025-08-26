import { BookingData } from '../types';
import { sendBookingToTelegram } from './telegram/sendBooking';
import { CalendarService } from './calendar.service';
import { v4 as uuidv4 } from 'uuid';

export class BookingService {
  private static instance: BookingService;
  private calendarService: CalendarService;

  private constructor(calendarService: CalendarService) {
    this.calendarService = calendarService;
  }

  public static getInstance(calendarService?: CalendarService): BookingService {
    if (!BookingService.instance) {
      if (!calendarService) {
        calendarService = CalendarService.getInstance();
      }
      BookingService.instance = new BookingService(calendarService);
    }
    return BookingService.instance;
  }

  public async createBooking(bookingData: Omit<BookingData, 'id' | 'status'>): Promise<BookingData> {
    const booking: BookingData = {
      ...bookingData,
      id: uuidv4(),
      status: 'pending'
    };

    try {
      // Add to calendar with pending status
      await this.calendarService.addEvent({
        title: `Pending: ${booking.name}`,
        summary: `Pending: ${booking.name}`,
        start: new Date(booking.date),
        end: new Date(new Date(booking.date).getTime() + 2 * 60 * 60 * 1000), // 2 hours duration
        description: JSON.stringify(booking)
      });

      // Send notification to Telegram
      await sendBookingToTelegram(booking);

      return booking;
    } catch (error) {
      console.error('Error creating booking:', error);
      throw error;
    }
  }

  public async confirmBooking(bookingId: string): Promise<BookingData | null> {
    try {
      // In a real implementation, you'd fetch the booking from a database
      const booking = await this.getBookingById(bookingId);
      
      if (!booking) return null;

      booking.status = 'confirmed';

      // Update calendar event
      await this.calendarService.updateEvent(bookingId, {
        summary: `Confirmed: ${booking.name}`
      });

      return booking;
    } catch (error) {
      console.error('Error confirming booking:', error);
      throw error;
    }
  }

  public async rejectBooking(bookingId: string): Promise<void> {
    try {
      // Remove the booking from calendar
      await this.calendarService.deleteEvent(bookingId);
    } catch (error) {
      console.error('Error rejecting booking:', error);
      throw error;
    }
  }

  private async getBookingById(bookingId: string): Promise<BookingData | null> {
    try {
      // Try to get from the existing bookingService first (local storage or cache)
      import('../services/booking/index').then(({ getBookingById: getLocalBooking }) => {
        const localBooking = getLocalBooking(bookingId);
        if (localBooking) {
          return localBooking;
        }
      }).catch(() => {
        // Fallback if local service fails
      });

      // Fallback to API call if not found locally
      const API_URL = '/api'; // Use relative URL to work with Vite proxy
      
      const response = await fetch(`${API_URL}/bookings/${bookingId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          return null; // Booking not found
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const booking = await response.json();
      return booking;
    } catch (error) {
      console.error(`Error retrieving booking ${bookingId}:`, error);
      return null;
    }
  }
}

// Export a singleton instance with the Calendar service
export const bookingService = BookingService.getInstance();
