import React, { useEffect, useState } from 'react';
import { getDayAvailability } from '../../services/calendar/availability';
import { BookingSlot } from '../../types/index';

interface TimeSelectorProps {
  date: { format: (format: string) => string }; // Dayjs-like interface
  selectedTimes: string[];
  onTimeSelect: (times: string[]) => void;
}

export const TimeSelector: React.FC<TimeSelectorProps> = ({
  date,
  selectedTimes,
  onTimeSelect
}) => {
  const [slots, setSlots] = useState<BookingSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSlots = async () => {
      try {
        setLoading(true);
        const dateStr = date.format('YYYY-MM-DD');
        const response = await getDayAvailability(dateStr);
        setSlots(response.slots || []);
        setError(null);
      } catch (err) {
        setError('Ошибка при загрузке доступного времени');
        console.error('Error fetching slots:', err);
      } finally {
        setLoading(false);
      }
    };

    if (date) {
      fetchSlots();
    }
  }, [date]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-700 text-center">{error}</p>
      </div>
    );
  }

  if (!slots.length) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <p className="text-yellow-700 text-center">Нет доступных слотов на выбранную дату</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-4">Выберите время</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {slots.map((slot) => (
          <button
            key={slot.startTime}
            onClick={() => {
              if (!slot.available) return;
              const isSelected = selectedTimes.includes(slot.startTime);
              const newTimes = isSelected
                ? selectedTimes.filter(t => t !== slot.startTime)
                : [...selectedTimes, slot.startTime].sort();
              onTimeSelect(newTimes);
            }}
            disabled={!slot.available}
            className={`
              p-3 rounded-lg text-center font-medium transition-all duration-200
              ${
                selectedTimes.includes(slot.startTime)
                  ? 'bg-blue-600 text-white transform scale-105 shadow-md'
                  : slot.available
                  ? 'bg-white border border-gray-300 text-gray-900 hover:bg-blue-50 hover:border-blue-300 hover:transform hover:scale-105'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }
            `}
          >
            {slot.startTime}
          </button>
        ))}
      </div>
    </div>
  );
}; 