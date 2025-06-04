import React from 'react';
import DatePicker from 'react-datepicker';
import { format } from 'date-fns';
import { useCalendar } from '../../hooks/useCalendar';
import DayStatus from './DayStatus';
import LoadingSpinner from '../common/LoadingSpinner';
import { BookingSlot } from '../../types';
import "react-datepicker/dist/react-datepicker.css";

interface CalendarProps {
  selectedDate: Date | null;
  onChange: (date: Date | null) => void;
}

export default function Calendar({ selectedDate, onChange }: CalendarProps) {
  const { loading, availability, fetchAvailability } = useCalendar();

  // Функция для получения класса в зависимости от доступности
  const getAvailabilityClass = React.useCallback((date: Date) => {
    if (loading) return '';

    const dateStr = format(date, 'yyyy-MM-dd');
    const dayAvailability = availability[dateStr];

    // Если нет информации о доступности
    if (!dayAvailability) return '';

    // Если есть слоты, проверяем их доступность
    if (dayAvailability.slots && dayAvailability.slots.length > 0) {
      const availableSlots = dayAvailability.slots.filter((slot: BookingSlot) => slot.available).length;
      if (availableSlots === 0) return 'bg-red-100 text-red-800 hover:bg-red-200';
      if (availableSlots < dayAvailability.slots.length) return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
      return 'bg-green-100 text-green-800 hover:bg-green-200';
    }

    // Если нет слотов, используем общую доступность
    return dayAvailability.isAvailable
      ? 'bg-green-100 text-green-800 hover:bg-green-200'
      : 'bg-red-100 text-red-800 hover:bg-red-200';
  }, [loading, availability]);

  // Обработчик изменения даты
  const handleDateChange = React.useCallback(async (date: Date | null) => {
    if (date) {
      await fetchAvailability(date);
    }
    onChange(date);
  }, [fetchAvailability, onChange]);

  return (
    <div className="calendar-wrapper">
      <DatePicker
        selected={selectedDate}
        onChange={handleDateChange}
        dayClassName={getAvailabilityClass}
        minDate={new Date()}
        inline
        calendarClassName="custom-calendar"
        renderDayContents={(day, date) => (
          <DayStatus
            day={day}
            isAvailable={date ? availability[format(date, 'yyyy-MM-dd')]?.isAvailable : undefined}
            slots={date ? availability[format(date, 'yyyy-MM-dd')]?.slots : undefined}
          />
        )}
      />
      {loading && <LoadingSpinner />}
    </div>
  );
}