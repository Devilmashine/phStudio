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
