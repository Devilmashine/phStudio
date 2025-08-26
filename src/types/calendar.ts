import { AvailabilityState } from './index';

export interface TimeSlot {
  time: string;
  isBooked: boolean;
}

export interface DayAvailability {
  date: string;
  isAvailable: boolean;
  status: AvailabilityState;
  slots?: TimeSlot[];
}

export interface CalendarEvent {
  start: { dateTime?: string; date?: string };
  end: { dateTime?: string; date?: string };
}