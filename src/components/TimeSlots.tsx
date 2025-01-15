import React from 'react';
import { getTimeSlots } from '../services/calendar/slots';
import LoadingSpinner from './common/LoadingSpinner';
import { BookingSlot } from '../types';

interface TimeSlotsProps {
  date: Date;
  selectedTimes: string[];
  onSelectTime: (time: string) => void;
}

export default function TimeSlots({ date, selectedTimes, onSelectTime }: TimeSlotsProps) {
  const [slots, setSlots] = React.useState<BookingSlot[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchSlots = async () => {
      try {
        setLoading(true);
        setError(null);

        // Преобразуем дату в строку в формате YYYY-MM-DD
        const dateStr = date.toISOString().split('T')[0];

        // Получаем доступные слоты
        const availableSlots = await getTimeSlots(dateStr);
        setSlots(availableSlots);
      } catch (err) {
        console.error('Error fetching slots:', err);
        setError('Не удалось загрузить доступные слоты. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    fetchSlots();
  }, [date]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      {slots.map((slot) => {
        const isSelected = selectedTimes.includes(slot.startTime);
        return (
          <button
            key={slot.startTime}
            onClick={() => onSelectTime(slot.startTime)}
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
}