import { useState, useCallback } from 'react';
import { format, addHours } from 'date-fns';
import { getAvailableSlots, AvailabilityState } from '../services/google/calendar';
import { DayAvailability, BookingSlot } from '../types';

export function useCalendar() {
  const [loading, setLoading] = useState(false);
  const [availability, setAvailability] = useState<Record<string, DayAvailability>>({});

  const fetchAvailability = useCallback(async (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    
    if (availability[dateStr]) {
      return availability[dateStr];
    }

    setLoading(true);
    try {
      const events = await getAvailableSlots(dateStr);
      const isAvailable = calculateDayAvailability(events);
      
      const slots: BookingSlot[] = events.map(event => {
        const startTime = event.time;
        const endTime = format(
          addHours(new Date(`${dateStr}T${startTime}`), 1), 
          'HH:mm'
        );

        return {
          date: dateStr,
          startTime,
          endTime,
          available: event.isBookable,
          bookedPercentage: event.bookedPercentage,
          state: event.state
        };
      });

      const dayAvailability: DayAvailability = {
        date: dateStr,
        isAvailable,
        slots
      };

      setAvailability(prev => ({
        ...prev,
        [dateStr]: dayAvailability
      }));
      
      return dayAvailability;
    } catch (error) {
      console.error('Error fetching availability:', error);
      const errorAvailability: DayAvailability = {
        date: dateStr,
        isAvailable: false,
        slots: []
      };
      return errorAvailability;
    } finally {
      setLoading(false);
    }
  }, [availability]);

  return {
    loading,
    availability,
    fetchAvailability
  };
}

function calculateDayAvailability(events: any[]): boolean {
  if (!events.length) return true;
  
  const totalSlotsBooked = events.filter(event => 
    event.state === AvailabilityState.FULLY_BOOKED
  ).length;

  // Если больше половины слотов заняты, день считается недоступным
  return totalSlotsBooked < events.length / 2;
}