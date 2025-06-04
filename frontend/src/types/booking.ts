export interface BookingSlot {
  id?: string;
  time: string;
  date: string;
  startTime: string;
  endTime: string;
  available: boolean;
  isAvailable: boolean;
  bookedPercentage: number;
  state?: 'available' | 'booked';
}

export interface BookingFormData {
  name: string;
  phone: string;
  service: string;
  totalPrice: number;
  comment?: string;
  date?: string;
  times?: string[];
}

export interface BookingResponse {
  message: string;
  calendar_links: (string | null)[];
}

export enum DateAvailabilityStatusType {
  AVAILABLE = 'AVAILABLE',
  PARTIALLY_BOOKED = 'PARTIALLY_BOOKED',
  FULLY_BOOKED = 'FULLY_BOOKED',
  ERROR = 'ERROR'
}

export interface DayAvailability {
  date: string;
  isAvailable: boolean;
  status: DateAvailabilityStatusType;
  slots: BookingSlot[];
} 