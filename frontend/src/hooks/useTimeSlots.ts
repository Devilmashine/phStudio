import { useState, useCallback } from 'react';
import { format, addHours } from 'date-fns';
import { getAvailableSlots } from '../services/google/calendar';
import { BookingSlot } from '../types';

export function useTimeSlots() {
  const [loading, setLoading] = useState(false);
  const [slots, setSlots] = useState<Record<string, BookingSlot[]>>({});

  const fetchTimeSlots = useCallback(async (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    
    if (slots[dateStr]) {
      return slots[dateStr];
    }

    setLoading(true);
    try {
      const events = await getAvailableSlots(dateStr);
      const timeSlots: BookingSlot[] = events.map(event => {
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
      
      setSlots(prev => ({
        ...prev,
        [dateStr]: timeSlots
      }));
      
      return timeSlots;
    } catch (error) {
      console.error('Error fetching time slots:', error);
      return [];
    } finally {
      setLoading(false);
    }
  }, [slots]);

  return {
    loading,
    slots,
    fetchTimeSlots
  };
}