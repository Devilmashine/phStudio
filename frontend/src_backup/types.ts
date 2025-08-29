export interface PricingPackage {
  id: number;
  name: string;
  price: number;
  duration: string;
  description: string;
  features: string[];
  recommended: boolean;
}

export interface BookingSlot {
  bookedPercentage: number;
  date: string;
  startTime: string;
  endTime: string;
  available: boolean;
}

export interface DayAvailability {
  date: string;
  isAvailable: boolean;
  slots?: BookingSlot[];
}

export interface TimeSlot {
  time: string;
  isBooked: boolean;
}

export interface BookingData {
  date: string;
  times: string[];
  name: string;
  phone: string;
  totalPrice: number;
  id?: string;
  eventId?: string;
  clientChatId?: string;
  status?: 'pending' | 'confirmed' | 'cancelled';
}

export interface CalendarEvent {
  id: string;
  start: {
    dateTime?: string;
    date?: string;
  };
  end: {
    dateTime?: string;
    date?: string;
  };
}

export interface StudioFeature {
  id: string;
  icon: string;
  title: string;
  description: string;
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
