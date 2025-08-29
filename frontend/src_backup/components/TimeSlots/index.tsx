import { FC, useEffect, useCallback } from 'react';
import TimeSlotGrid from './TimeSlotGrid';
import { useTimeSlots } from '../../hooks/useTimeSlots';

interface TimeSlotsProps {
  date: Date;
  selectedTimes: string[];
  onSelectTime: (time: string) => void;
}

const TimeSlots: FC<TimeSlotsProps> = ({ date, selectedTimes, onSelectTime }) => {
  const { slots, loading, fetchTimeSlots } = useTimeSlots();

  // Оборачиваем handleFetchSlots в useCallback
  const handleFetchSlots = useCallback(async () => {
    try {
      await fetchTimeSlots(date);
    } catch (err) {
      console.error('Failed to fetch time slots', err);
    }
  }, [date, fetchTimeSlots]);

  useEffect(() => {
    handleFetchSlots();
  }, [handleFetchSlots]);

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