/**
 * Zustand Store Configuration
 * Centralized state management following enhanced CRM architecture
 */

export { default as useBookingStore } from './bookingStore';
export { default as useEmployeeStore } from './employeeStore';
export { default as useUIStore } from './uiStore';
export { default as useAuthStore } from './authStore';

// Export store types
export type * from './types';
