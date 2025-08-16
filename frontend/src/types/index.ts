export enum AvailabilityState {
  AVAILABLE = 'available',
  PARTIALLY_BOOKED = 'partially-booked',
  FULLY_BOOKED = 'fully-booked',
  UNKNOWN = 'unknown'
}

export interface Studio {
  id: number;
  name: string;
  description: string;
  size: string;
  pricePerHour: number;
  features: StudioFeature[];
  equipment: string[];
  images: string[];
}

export interface StudioFeature {
  id: string;
  title: string;
  description: string;
  icon: string;
}

export interface TimeSlot {
  time: string;
  isBooked: boolean;
  bookedPercentage?: number;
  state?: AvailabilityState;
}

export interface BookingSlot {
  date: string;
  startTime: string;
  endTime: string;
  available: boolean;
  bookedPercentage: number;
  state?: AvailabilityState;
}

export interface BookingData {
  id?: string;
  date: string;
  times: string[];
  name: string;
  phone: string;
  totalPrice: number;
  service?: string;
  status?: 'pending' | 'confirmed' | 'cancelled';
  studioId?: number;
}

export interface DayAvailability {
  date: string;
  isAvailable: boolean;
  status: AvailabilityState;
  slots: BookingSlot[];
}