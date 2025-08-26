import { FC } from 'react';
import { BookingSlot } from '../../types';

interface DayStatusProps {
  day: number;
  isAvailable?: boolean;
  slots?: BookingSlot[];
  isPast?: boolean;
}

const DayStatus: FC<DayStatusProps> = ({ day, isAvailable, slots, isPast }) => {
  // Если дата в прошлом, показываем серым цветом
  if (isPast) {
    return <div className="text-gray-400">{day}</div>;
  }

  // Если нет информации о доступности, показываем обычным цветом
  if (isAvailable === undefined || !slots) {
    return <div className="text-gray-700">{day}</div>;
  }

  // Просто отображаем день без дополнительной информации
  return <div>{day}</div>;
};

export default DayStatus;