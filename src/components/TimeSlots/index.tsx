import { FC, useEffect } from 'react';
import TimeSlotGrid from './TimeSlotGrid';
import { useTimeSlots } from '../../hooks/useTimeSlots';

interface TimeSlotsProps {
  date: Date;
  selectedTimes: string[];
  onSelectTime: (time: string) => void;
}

const TimeSlots: FC<TimeSlotsProps> = ({ date, selectedTimes, onSelectTime }) => {
  const { slots, loading, fetchTimeSlots } = useTimeSlots();

  // Fetch slots when component mounts or date changes
  const handleFetchSlots = async () => {
    try {
      await fetchTimeSlots(date);
    } catch (err) {
      console.error('Failed to fetch time slots', err);
    }
  };

  // Fetch slots on mount and when date changes
  useEffect(() => {
    handleFetchSlots();
  }, [date]);

  if (loading) return <div>Загрузка...</div>;

  // Get slots for the specific date
  const dateSlots = slots[date.toISOString().split('T')[0]] || [];

  return (
    <TimeSlotGrid
      slots={dateSlots}
      selectedTimes={selectedTimes}
      onTimeSelect={onSelectTime}
    />
  );
};

export default TimeSlots;