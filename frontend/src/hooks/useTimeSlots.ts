import { useState, useCallback } from 'react';
import { format } from 'date-fns';
import { getAvailableSlots } from '../data/availability';
import { BookingSlot } from '../types/index';

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
      const dayAvailability = await getAvailableSlots(dateStr);
      const timeSlots = dayAvailability.slots;
      
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