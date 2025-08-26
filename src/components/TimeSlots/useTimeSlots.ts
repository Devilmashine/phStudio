import { useState, useEffect } from 'react';
import { getTimeSlots } from '../../services/calendar/slots';

interface TimeSlot {
  time: string;
  isBooked: boolean;
}

export function useTimeSlots(date: Date) {
  const [slots, setSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSlots = async () => {
      try {
        setLoading(true);
        setError(null);
        const dateStr = date.toISOString().split('T')[0];
        const availableSlots = await getTimeSlots(dateStr);
        setSlots(availableSlots.timeSlots);
      } catch (err) {
        setError('Failed to load available time slots');
        console.error('Error fetching slots:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSlots();
  }, [date]);

  return { slots, loading, error };
}