import React from 'react';
import TimeSlotButton from './TimeSlotButton';
import { BookingSlot } from '../../types/index';

interface TimeSlotGridProps {
  slots: BookingSlot[];
  selectedTimes: string[];
  onTimeSelect: (time: string) => void;
}

const TimeSlotGrid: React.FC<TimeSlotGridProps> = ({ 
  slots, 
  selectedTimes, 
  onTimeSelect 
}) => {
  return (
    <div className="grid grid-cols-4 gap-2">
      {slots.map((slot) => (
        <TimeSlotButton
          key={slot.startTime}
          time={slot.startTime}
          isBooked={!slot.available}
          isSelected={selectedTimes.includes(slot.startTime)}
          bookedPercentage={slot.bookedPercentage}
          onSelect={() => onTimeSelect(slot.startTime)}
        />
      ))}
    </div>
  );
};

export default TimeSlotGrid;