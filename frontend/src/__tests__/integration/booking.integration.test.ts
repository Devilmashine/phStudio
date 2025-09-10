/**
 * Booking Integration Tests
 * Тесты интеграции frontend-backend для бронирований
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from '@jest/globals';
import { enhancedBookingApi } from '../../services/api/enhancedBookingApi';
import { enhancedAuthApi } from '../../services/api/enhancedAuthApi';
import { CreateBookingRequest, BookingState, SpaceType, BookingPriority } from '../../stores/types';

// Mock API responses
const mockBookingResponse = {
  id: 1,
  booking_reference: 'BK-2024-001',
  booking_date: '2024-01-15',
  start_time: '2024-01-15T10:00:00.000Z',
  end_time: '2024-01-15T12:00:00.000Z',
  duration_hours: 2,
  state: BookingState.PENDING,
  state_history: [],
  client_name: 'Иван Петров',
  client_phone: '+7 (999) 123-45-67',
  client_phone_normalized: '+79991234567',
  client_email: 'ivan@example.com',
  space_type: SpaceType.MAIN_STUDIO,
  equipment_requested: ['professional_lighting'],
  special_requirements: 'Нужен белый фон',
  base_price: 4000,
  equipment_price: 1000,
  discount_amount: 0,
  total_price: 5000,
  payment_status: 'pending',
  source: 'website',
  notes: 'Тестовое бронирование',
  internal_notes: '',
  priority: BookingPriority.NORMAL,
  created_at: '2024-01-15T09:00:00.000Z',
  updated_at: '2024-01-15T09:00:00.000Z',
  created_by: 1,
  updated_by: 1,
  version: 1,
};

const mockAuthResponse = {
  access_token: 'mock-jwt-token',
  refresh_token: 'mock-refresh-token',
  employee: {
    id: 1,
    employee_id: 'EMP-001',
    username: 'admin',
    email: 'admin@studio.com',
    role: 'admin',
    status: 'active',
    full_name: 'Администратор',
    phone: '+7 (999) 000-00-00',
    department: 'Management',
    position: 'Studio Manager',
    hire_date: '2024-01-01',
    timezone: 'Europe/Moscow',
    language: 'ru',
    mfa_enabled: false,
    password_changed_at: '2024-01-01T00:00:00.000Z',
    last_login: '2024-01-15T09:00:00.000Z',
    last_activity: '2024-01-15T09:00:00.000Z',
    failed_login_attempts: 0,
    created_at: '2024-01-01T00:00:00.000Z',
    updated_at: '2024-01-15T09:00:00.000Z',
    version: 1,
  },
  mfa_required: false,
  expires_in: 3600,
};

// Mock fetch
global.fetch = jest.fn();

describe('Booking Integration Tests', () => {
  beforeAll(() => {
    // Setup test environment
    process.env.VITE_API_URL = 'http://localhost:8000';
  });

  afterAll(() => {
    // Cleanup
    jest.restoreAllMocks();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication Flow', () => {
    it('should authenticate user and get access token', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockAuthResponse, success: true }),
      });

      const result = await enhancedAuthApi.login({
        username: 'admin',
        password: 'password123',
      });

      expect(result).toEqual(mockAuthResponse);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            username: 'admin',
            password: 'password123',
          }),
        })
      );
    });

    it('should handle authentication errors', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ 
          message: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS',
          success: false 
        }),
      });

      await expect(
        enhancedAuthApi.login({
          username: 'admin',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('Booking CRUD Operations', () => {
    it('should create a new booking', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockBookingResponse, success: true }),
      });

      const bookingData: CreateBookingRequest = {
        client_name: 'Иван Петров',
        client_phone: '+7 (999) 123-45-67',
        client_email: 'ivan@example.com',
        booking_date: '2024-01-15',
        start_time: '2024-01-15T10:00:00.000Z',
        end_time: '2024-01-15T12:00:00.000Z',
        space_type: SpaceType.MAIN_STUDIO,
        equipment_requested: ['professional_lighting'],
        special_requirements: 'Нужен белый фон',
        notes: 'Тестовое бронирование',
        priority: BookingPriority.NORMAL,
      };

      const result = await enhancedBookingApi.createBooking(bookingData);

      expect(result).toEqual(mockBookingResponse);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(bookingData),
        })
      );
    });

    it('should get booking by ID', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockBookingResponse, success: true }),
      });

      const result = await enhancedBookingApi.getBooking(1);

      expect(result).toEqual(mockBookingResponse);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings/1',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should get paginated bookings list', async () => {
      const mockPaginatedResponse = {
        items: [mockBookingResponse],
        total: 1,
        page: 1,
        pages: 1,
        per_page: 20,
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPaginatedResponse,
      });

      const result = await enhancedBookingApi.getBookings({
        page: 1,
        per_page: 20,
      });

      expect(result).toEqual(mockPaginatedResponse);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should update booking', async () => {
      const updatedBooking = { ...mockBookingResponse, client_name: 'Петр Иванов' };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: updatedBooking, success: true }),
      });

      const result = await enhancedBookingApi.updateBooking(1, {
        client_name: 'Петр Иванов',
      });

      expect(result).toEqual(updatedBooking);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings/1',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ client_name: 'Петр Иванов' }),
        })
      );
    });

    it('should transition booking state', async () => {
      const confirmedBooking = { ...mockBookingResponse, state: BookingState.CONFIRMED };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: confirmedBooking, success: true }),
      });

      const result = await enhancedBookingApi.transitionBookingState(1, {
        new_state: BookingState.CONFIRMED,
        notes: 'Подтверждено администратором',
      });

      expect(result).toEqual(confirmedBooking);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings/1/state',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            new_state: BookingState.CONFIRMED,
            notes: 'Подтверждено администратором',
          }),
        })
      );
    });

    it('should cancel booking', async () => {
      const cancelledBooking = { ...mockBookingResponse, state: BookingState.CANCELLED };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: cancelledBooking, success: true }),
      });

      const result = await enhancedBookingApi.cancelBooking(1, 'Клиент отменил');

      expect(result).toEqual(cancelledBooking);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings/1/cancel',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ reason: 'Клиент отменил' }),
        })
      );
    });

    it('should delete booking', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await enhancedBookingApi.deleteBooking(1);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings/1',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });

  describe('Booking Analytics', () => {
    it('should get booking analytics', async () => {
      const mockAnalytics = {
        total_bookings: 100,
        completed_bookings: 80,
        pending_bookings: 15,
        cancelled_bookings: 5,
        total_revenue: 500000,
        average_price: 5000,
        unique_clients: 75,
        completion_rate: 80,
        revenue_by_month: [
          { month: '2024-01', revenue: 100000 },
          { month: '2024-02', revenue: 120000 },
        ],
        bookings_by_state: [
          { state: 'completed', count: 80 },
          { state: 'pending', count: 15 },
        ],
        popular_time_slots: [
          { hour: 10, count: 25 },
          { hour: 14, count: 30 },
        ],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockAnalytics, success: true }),
      });

      const result = await enhancedBookingApi.getBookingAnalytics({
        start_date: '2024-01-01',
        end_date: '2024-01-31',
      });

      expect(result).toEqual(mockAnalytics);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/bookings/analytics/summary',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should get dashboard stats', async () => {
      const mockStats = {
        total_bookings: 50,
        completed_bookings: 40,
        pending_bookings: 8,
        cancelled_bookings: 2,
        total_revenue: 250000,
        average_price: 5000,
        completion_rate: 80,
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockStats, success: true }),
      });

      const result = await enhancedBookingApi.getDashboardStats();

      expect(result).toEqual(mockStats);
    });
  });

  describe('Availability Checking', () => {
    it('should check time slot availability', async () => {
      const mockAvailability = {
        available: true,
        conflicts: [],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockAvailability, success: true }),
      });

      const result = await enhancedBookingApi.checkAvailability({
        date: '2024-01-15',
        start_time: '10:00',
        end_time: '12:00',
        space_type: 'main_studio',
      });

      expect(result).toEqual(mockAvailability);
    });

    it('should get bookings for specific date', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [mockBookingResponse], success: true }),
      });

      const result = await enhancedBookingApi.getBookingsForDate('2024-01-15');

      expect(result).toEqual([mockBookingResponse]);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(
        enhancedBookingApi.getBooking(1)
      ).rejects.toThrow('Network error');
    });

    it('should handle API errors', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ 
          message: 'Validation error',
          code: 'VALIDATION_ERROR',
          field_errors: {
            client_name: ['Name is required'],
            client_phone: ['Invalid phone format'],
          },
          success: false 
        }),
      });

      await expect(
        enhancedBookingApi.createBooking({
          client_name: '',
          client_phone: 'invalid',
          booking_date: '2024-01-15',
          start_time: '2024-01-15T10:00:00.000Z',
          end_time: '2024-01-15T12:00:00.000Z',
          space_type: SpaceType.MAIN_STUDIO,
        })
      ).rejects.toThrow('Validation error');
    });

    it('should handle 404 errors', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ 
          message: 'Booking not found',
          code: 'NOT_FOUND',
          success: false 
        }),
      });

      await expect(
        enhancedBookingApi.getBooking(999)
      ).rejects.toThrow('Booking not found');
    });
  });

  describe('Data Validation', () => {
    it('should validate booking data before sending', async () => {
      const invalidBookingData = {
        client_name: '', // Invalid: empty name
        client_phone: 'invalid', // Invalid: wrong format
        booking_date: '2024-01-15',
        start_time: '2024-01-15T10:00:00.000Z',
        end_time: '2024-01-15T12:00:00.000Z',
        space_type: SpaceType.MAIN_STUDIO,
      };

      // Should not make API call for invalid data
      await expect(
        enhancedBookingApi.createBooking(invalidBookingData as any)
      ).rejects.toThrow();
    });
  });
});
