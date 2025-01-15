import { useState, useCallback } from 'react';
import { format } from 'date-fns';
import { getDayAvailability } from '../../../services/calendar/availability';
import { DayAvailability } from '../../../types';

// Тип для доступности
type Availability = Record<string, boolean>;

export function useCalendarAvailability() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availability, setAvailability] = useState<Availability>({});
  const [dayDetails, setDayDetails] = useState<Record<string, DayAvailability>>({});

  // Функция для получения доступности на конкретную дату
  const fetchAvailability = useCallback(async (date: Date) => {
    setLoading(true);
    setError(null); // Сброс ошибки перед новым запросом

    try {
      const dateStr = format(date, 'yyyy-MM-dd');
      const dayAvailability = await getDayAvailability(dateStr);

      // Обновляем состояние с новыми данными
      setAvailability((prev) => ({
        ...prev,
        [dateStr]: dayAvailability.isAvailable,
      }));

      // Сохраняем полные данные о дне
      setDayDetails((prev) => ({
        ...prev,
        [dateStr]: dayAvailability,
      }));
    } catch (err) {
      console.error('Error fetching availability:', err);
      setError('Не удалось загрузить данные о доступности. Пожалуйста, попробуйте позже.');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    availability,
    dayDetails,
    error,
    fetchAvailability,
  };
}