import { useState, useCallback } from 'react';
import { format } from 'date-fns';
import { getAvailableSlots } from '../data/availability';
import { AvailabilityState, DayAvailability } from '../types/index';

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
      const dayAvailability = await getAvailableSlots(dateStr);

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
        slots: [],
        status: AvailabilityState.UNKNOWN
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