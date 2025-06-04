import { addHours } from 'date-fns';
import { CALENDAR_CONFIG } from '../../config/calendar';

const BASE_URL = 'https://www.googleapis.com/calendar/v3';

// Availability states for more granular representation
export enum AvailabilityState {
  FULLY_AVAILABLE = 'fully_available', // Slot is completely free
  PARTIALLY_BOOKED = 'partially_booked', // Some time in the slot is booked
  FULLY_BOOKED = 'fully_booked' // Entire slot is booked
}

// Types
interface BusySlot {
  start: string;
  end: string;
}

interface AvailableSlot {
  time: string;
  state: AvailabilityState;
  bookedPercentage: number;
  isBookable: boolean; // New field to explicitly indicate if slot can be booked
  events?: { // Optional field to show which events are causing booking restrictions
    summary?: string;
    start: string;
    end: string;
  }[];
}

class CalendarError extends Error {
  code?: string;
  details?: any;

  constructor(message: string, details?: { code?: string; details?: any }) {
    super(message);
    this.name = 'CalendarError';
    if (details) {
      this.code = details.code;
      this.details = details.details;
    }
  }
}

async function getAccessToken(): Promise<string> {
  try {
    // Placeholder for actual token generation
    // In a real-world scenario, this would use service account credentials
    const accessToken = 'your_access_token_here';
    return accessToken;
  } catch (error) {
    console.error('Error getting access token:', error);
    throw new CalendarError('Failed to get access token');
  }
}

function localToUTC(date: string, time: string): Date {
  const [hours, minutes] = time.split(':').map(Number);
  const localDateTime = new Date(`${date}T${time}:00+03:00`);
  return new Date(Date.UTC(
    localDateTime.getFullYear(), 
    localDateTime.getMonth(), 
    localDateTime.getDate(), 
    hours, 
    minutes
  ));
}

async function fetchCalendarEvents(start: string, end: string): Promise<any[]> {
  try {
    const requestParams = new URLSearchParams({
      timeMin: start,
      timeMax: end,
      singleEvents: 'true',
      orderBy: 'startTime'
    });

    const accessToken = await getAccessToken();

    const response = await fetch(
      `${BASE_URL}/calendars/${encodeURIComponent(CALENDAR_CONFIG.calendarId)}/events?${requestParams}`, 
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        }
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Failed to fetch calendar events:', {
        status: response.status,
        data: errorData,
        request: start
      });
      throw new CalendarError('Failed to fetch calendar events', { details: errorData });
    }

    const data = await response.json();
    return data.items || [];
  } catch (error) {
    console.error('Error fetching calendar events:', error);
    throw error instanceof CalendarError ? error : new CalendarError('Failed to fetch calendar events');
  }
}

export async function getAvailableSlots(date: string): Promise<AvailableSlot[]> {
  try {
    // Fetch real calendar events
    const events = await fetchCalendarEvents(
      `${date}T00:00:00Z`, 
      `${date}T23:59:59Z`
    );

    // Define available time slots
    const availableTimeSlots = [
      '09:00', '10:00', '11:00', '12:00', 
      '13:00', '14:00', '15:00', '16:00', 
      '17:00', '18:00', '19:00', '20:00'
    ];

    // Convert events to busy slots with detailed logging
    const busySlots: BusySlot[] = events.map(event => {
      const start = event.start.dateTime || event.start.date;
      const end = event.end.dateTime || event.end.date;
      
      console.log('Existing Event:', {
        summary: event.summary,
        start,
        end
      });

      return { start, end };
    });

    // Mark slots with their availability state
    const availableSlots: AvailableSlot[] = availableTimeSlots.map((slotTime: string) => {
      const slotStart = localToUTC(date, slotTime);
      const slotEnd = addHours(slotStart, 1);

      // Calculate booking details for the slot
      const slotOverlaps = busySlots.filter(busySlot => {
        const busyStart = new Date(busySlot.start);
        const busyEnd = new Date(busySlot.end);

        // Precise time overlap detection
        const slotStartUTC = slotStart.getTime();
        const slotEndUTC = slotEnd.getTime();
        const busyStartUTC = busyStart.getTime();
        const busyEndUTC = busyEnd.getTime();

        return (slotStartUTC < busyEndUTC && slotEndUTC > busyStartUTC);
      });

      // Calculate percentage of slot booked
      let bookedPercentage = 0;
      const overlappingEvents: AvailableSlot['events'] = [];
      if (slotOverlaps.length > 0) {
        const slotDuration = 60 * 60 * 1000; // 1 hour in milliseconds
        const bookedDuration = slotOverlaps.reduce((total, overlap) => {
          const busyStart = new Date(overlap.start);
          const busyEnd = new Date(overlap.end);
          
          // Calculate overlap duration
          const overlapStart = Math.max(busyStart.getTime(), slotStart.getTime());
          const overlapEnd = Math.min(busyEnd.getTime(), slotEnd.getTime());
          
          // Store events causing overlap
          overlappingEvents.push({
            start: busyStart.toISOString(),
            end: busyEnd.toISOString()
          });
          
          return total + Math.max(0, overlapEnd - overlapStart);
        }, 0);

        bookedPercentage = Math.round((bookedDuration / slotDuration) * 100);
      }

      // Determine availability state
      let state: AvailabilityState;
      let isBookable: boolean;
      if (bookedPercentage === 0) {
        state = AvailabilityState.FULLY_AVAILABLE;
        isBookable = true;
      } else if (bookedPercentage === 100) {
        state = AvailabilityState.FULLY_BOOKED;
        isBookable = false;
      } else {
        state = AvailabilityState.PARTIALLY_BOOKED;
        isBookable = true;
      }

      // Log detailed slot information
      console.log('Slot Availability:', {
        time: slotTime,
        state,
        bookedPercentage,
        isBookable
      });

      return {
        time: slotTime,
        state,
        bookedPercentage,
        isBookable,
        events: overlappingEvents
      };
    });

    console.log('Available Slots:', availableSlots);

    return availableSlots;
  } catch (error) {
    console.error('Error fetching time slots:', error);
    
    // Fallback to fully available slots if there's an error
    return [
      '09:00', '10:00', '11:00', '12:00', 
      '13:00', '14:00', '15:00', '16:00', 
      '17:00', '18:00', '19:00', '20:00'
    ].map(time => ({
      time,
      state: AvailabilityState.FULLY_AVAILABLE,
      bookedPercentage: 0,
      isBookable: true
    }));
  }
}

export async function getTimeSlots(date: string): Promise<AvailableSlot[]> {
  return getAvailableSlots(date);
}