/**
 * Enhanced Booking Store
 * Zustand store для управления бронированиями с интеграцией enhanced backend
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  EnhancedBooking,
  BookingStoreState,
  CreateBookingRequest,
  UpdateBookingRequest,
  BookingStateTransitionRequest,
  BookingFilters,
  BookingState,
  ApiResponse,
  PaginatedResponse
} from './types';
import { enhancedBookingApi } from '../services/api/enhancedBookingApi';

interface BookingStoreActions {
  // Data fetching
  fetchBookings: (filters?: BookingFilters, page?: number) => Promise<void>;
  fetchBooking: (id: number) => Promise<void>;
  refreshBookings: () => Promise<void>;
  
  // CRUD operations
  createBooking: (data: CreateBookingRequest) => Promise<EnhancedBooking>;
  updateBooking: (id: number, data: UpdateBookingRequest) => Promise<EnhancedBooking>;
  transitionBookingState: (id: number, data: BookingStateTransitionRequest) => Promise<EnhancedBooking>;
  cancelBooking: (id: number, reason?: string) => Promise<EnhancedBooking>;
  deleteBooking: (id: number) => Promise<void>;
  
  // State management
  setSelectedBooking: (booking: EnhancedBooking | null) => void;
  setFilters: (filters: Partial<BookingFilters>) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  
  // UI state
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Real-time updates
  handleBookingEvent: (event: any) => void;
  
  // Cache management
  invalidateCache: () => void;
  updateBookingInCache: (booking: EnhancedBooking) => void;
  removeBookingFromCache: (id: number) => void;
}

type BookingStore = BookingStoreState & BookingStoreActions;

const initialState: BookingStoreState = {
  // Data
  bookings: [],
  selectedBooking: null,
  bookingFilters: {},
  
  // UI State
  loading: false,
  error: null,
  isCreating: false,
  isUpdating: false,
  
  // Pagination
  currentPage: 1,
  totalPages: 1,
  totalItems: 0,
  itemsPerPage: 20,
};

export const useBookingStore = create<BookingStore>()(
  devtools(
    immer(
      persist(
        (set, get) => ({
          ...initialState,

          // Data fetching
          fetchBookings: async (filters?: BookingFilters, page?: number) => {
            set((state) => {
              state.loading = true;
              state.error = null;
            });

            try {
              const currentPage = page || get().currentPage;
              const currentFilters = filters || get().bookingFilters;
              
              const response = await enhancedBookingApi.getBookings({
                ...currentFilters,
                page: currentPage,
                per_page: get().itemsPerPage,
              });

              set((state) => {
                state.bookings = response.items;
                state.currentPage = response.page;
                state.totalPages = response.pages;
                state.totalItems = response.total;
                state.bookingFilters = currentFilters;
                state.loading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при загрузке бронирований';
                state.loading = false;
              });
            }
          },

          fetchBooking: async (id: number) => {
            set((state) => {
              state.loading = true;
              state.error = null;
            });

            try {
              const booking = await enhancedBookingApi.getBooking(id);
              
              set((state) => {
                state.selectedBooking = booking;
                
                // Update booking in cache if it exists
                const existingIndex = state.bookings.findIndex(b => b.id === id);
                if (existingIndex !== -1) {
                  state.bookings[existingIndex] = booking;
                }
                
                state.loading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при загрузке бронирования';
                state.loading = false;
              });
            }
          },

          refreshBookings: async () => {
            const { bookingFilters, currentPage } = get();
            await get().fetchBookings(bookingFilters, currentPage);
          },

          // CRUD operations
          createBooking: async (data: CreateBookingRequest): Promise<EnhancedBooking> => {
            set((state) => {
              state.isCreating = true;
              state.error = null;
            });

            try {
              const booking = await enhancedBookingApi.createBooking(data);
              
              set((state) => {
                // Add to beginning of list
                state.bookings.unshift(booking);
                state.totalItems += 1;
                state.isCreating = false;
              });

              return booking;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при создании бронирования';
                state.isCreating = false;
              });
              throw error;
            }
          },

          updateBooking: async (id: number, data: UpdateBookingRequest): Promise<EnhancedBooking> => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              const booking = await enhancedBookingApi.updateBooking(id, data);
              
              set((state) => {
                // Update in cache
                const index = state.bookings.findIndex(b => b.id === id);
                if (index !== -1) {
                  state.bookings[index] = booking;
                }
                
                // Update selected booking if it's the same
                if (state.selectedBooking?.id === id) {
                  state.selectedBooking = booking;
                }
                
                state.isUpdating = false;
              });

              return booking;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при обновлении бронирования';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          transitionBookingState: async (id: number, data: BookingStateTransitionRequest): Promise<EnhancedBooking> => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              const booking = await enhancedBookingApi.transitionBookingState(id, data);
              
              set((state) => {
                // Update in cache
                const index = state.bookings.findIndex(b => b.id === id);
                if (index !== -1) {
                  state.bookings[index] = booking;
                }
                
                // Update selected booking if it's the same
                if (state.selectedBooking?.id === id) {
                  state.selectedBooking = booking;
                }
                
                state.isUpdating = false;
              });

              return booking;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при изменении статуса бронирования';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          cancelBooking: async (id: number, reason?: string): Promise<EnhancedBooking> => {
            return get().transitionBookingState(id, {
              new_state: BookingState.CANCELLED,
              reason,
            });
          },

          deleteBooking: async (id: number) => {
            set((state) => {
              state.loading = true;
              state.error = null;
            });

            try {
              await enhancedBookingApi.deleteBooking(id);
              
              set((state) => {
                state.bookings = state.bookings.filter(b => b.id !== id);
                state.totalItems -= 1;
                
                if (state.selectedBooking?.id === id) {
                  state.selectedBooking = null;
                }
                
                state.loading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при удалении бронирования';
                state.loading = false;
              });
              throw error;
            }
          },

          // State management
          setSelectedBooking: (booking: EnhancedBooking | null) => {
            set((state) => {
              state.selectedBooking = booking;
            });
          },

          setFilters: (filters: Partial<BookingFilters>) => {
            set((state) => {
              state.bookingFilters = { ...state.bookingFilters, ...filters };
              state.currentPage = 1; // Reset to first page when filters change
            });
          },

          clearFilters: () => {
            set((state) => {
              state.bookingFilters = {};
              state.currentPage = 1;
            });
          },

          setPage: (page: number) => {
            set((state) => {
              state.currentPage = page;
            });
          },

          // UI state
          setLoading: (loading: boolean) => {
            set((state) => {
              state.loading = loading;
            });
          },

          setError: (error: string | null) => {
            set((state) => {
              state.error = error;
            });
          },

          clearError: () => {
            set((state) => {
              state.error = null;
            });
          },

          // Real-time updates
          handleBookingEvent: (event: any) => {
            const { event_type, booking_id } = event;

            switch (event_type) {
              case 'BOOKING_CREATED':
                // Refresh bookings to get the new one
                get().refreshBookings();
                break;

              case 'BOOKING_UPDATED':
              case 'BOOKING_STATE_CHANGED':
                // Update specific booking
                get().fetchBooking(booking_id);
                break;

              case 'BOOKING_CANCELLED':
              case 'BOOKING_DELETED':
                set((state) => {
                  state.bookings = state.bookings.filter(b => b.id !== booking_id);
                  
                  if (state.selectedBooking?.id === booking_id) {
                    state.selectedBooking = null;
                  }
                });
                break;
            }
          },

          // Cache management
          invalidateCache: () => {
            set((state) => {
              state.bookings = [];
              state.selectedBooking = null;
            });
          },

          updateBookingInCache: (booking: EnhancedBooking) => {
            set((state) => {
              const index = state.bookings.findIndex(b => b.id === booking.id);
              if (index !== -1) {
                state.bookings[index] = booking;
              }
              
              if (state.selectedBooking?.id === booking.id) {
                state.selectedBooking = booking;
              }
            });
          },

          removeBookingFromCache: (id: number) => {
            set((state) => {
              state.bookings = state.bookings.filter(b => b.id !== id);
              
              if (state.selectedBooking?.id === id) {
                state.selectedBooking = null;
              }
            });
          },
        }),
        {
          name: 'booking-store',
          partialize: (state) => ({
            bookingFilters: state.bookingFilters,
            currentPage: state.currentPage,
            itemsPerPage: state.itemsPerPage,
          }),
        }
      )
    ),
    { name: 'BookingStore' }
  )
);

export default useBookingStore;
