import React from 'react';

interface TimeSlotButtonProps {
  time: string;
  isSelected: boolean;
  isBooked: boolean;
  onSelect: (time: string) => void;
}

const TimeSlotButton = React.memo(({
  time,
  isSelected,
  isBooked,
  onSelect
}: TimeSlotButtonProps) => {
  return (
    <button
      type="button"
      onClick={() => !isBooked && onSelect(time)}
      disabled={isBooked}
      className={`
        w-full p-2 rounded-lg text-sm font-medium 
        ${isBooked 
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-50' 
          : isSelected 
            ? 'bg-indigo-600 text-white' 
            : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100'
        }
      `}
    >
      {time}
    </button>
  );
});

TimeSlotButton.displayName = 'TimeSlotButton';

export default TimeSlotButton;