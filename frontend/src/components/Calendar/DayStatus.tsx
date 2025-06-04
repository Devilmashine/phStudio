import { FC } from 'react';
import { BookingSlot } from '../../types';

interface DayStatusProps {
  day: number;
  isAvailable?: boolean;
  slots?: BookingSlot[];
}

const DayStatus: FC<DayStatusProps> = ({ day, isAvailable, slots }) => {
  // Если нет информации о доступности
  if (isAvailable === undefined) {
    return <div className="text-gray-700">{day}</div>;
  }

  // Если есть слоты, показываем более детальную информацию
  if (slots && slots.length > 0) {
    const availableSlots = slots.filter(slot => slot.available).length;
    const totalSlots = slots.length;
    
    return (
      <div className="relative">
        <div>{day}</div>
        <div className="text-xs mt-1">
          {availableSlots}/{totalSlots}
        </div>
      </div>
    );
  }

  // Если нет слотов, показываем просто доступность
  return (
    <div className={isAvailable ? 'text-green-700' : 'text-red-700'}>
      {day}
    </div>
  );
};

export default DayStatus;