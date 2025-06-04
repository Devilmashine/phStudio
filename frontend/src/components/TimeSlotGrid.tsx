import React from 'react';
import { BookingSlot } from '../types';

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
    <div className="grid grid-cols-3 gap-4">
      {slots.map((slot) => {
        const isSelected = selectedTimes.includes(slot.startTime);
        return (
          <button
            key={slot.startTime}
            onClick={() => onTimeSelect(slot.startTime)}
            disabled={!slot.available}
            className={`
              p-3 rounded-lg text-center transition-colors
              ${!slot.available ? 'bg-gray-100 text-gray-400 cursor-not-allowed' :
                isSelected ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-300 hover:bg-gray-50'
              }
            `}
          >
            {slot.startTime}
          </button>
        );
      })}
    </div>
  );
};

TimeSlotGrid.displayName = 'TimeSlotGrid';

export default TimeSlotGrid;
