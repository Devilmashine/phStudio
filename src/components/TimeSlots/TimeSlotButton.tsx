import React from 'react';

interface TimeSlotButtonProps {
  time: string;
  isSelected: boolean;
  isBooked: boolean;
  bookedPercentage: number;
  onSelect: (time: string) => void;
}

const TimeSlotButton = React.memo(({
  time,
  isSelected,
  isBooked,
  bookedPercentage,
  onSelect
}: TimeSlotButtonProps) => {
  return (
    <div className="relative w-full">
      <button
        onClick={() => !isBooked && onSelect(time)}
        disabled={isBooked}
        className={`w-full p-2 rounded-lg text-sm font-medium relative z-10 ${
          isBooked
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-50'
            : isSelected
            ? 'bg-indigo-600 text-white'
            : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100'
        }`}
      >
        {time}
      </button>
      {bookedPercentage > 0 && bookedPercentage < 100 && (
        <div 
          className="absolute bottom-0 left-0 w-full h-1 bg-blue-200 rounded-b-lg overflow-hidden z-0"
          title={`Занято ${bookedPercentage}%`}
        >
          <div 
            className="h-full bg-blue-500" 
            style={{ width: `${bookedPercentage}%` }}
          />
        </div>
      )}
    </div>
  );
});

TimeSlotButton.displayName = 'TimeSlotButton';

export default TimeSlotButton;