import React, { useMemo, useCallback, useEffect } from 'react';
import DatePicker, { registerLocale } from 'react-datepicker';
import { format, isBefore, startOfDay } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useCalendar } from '../../hooks/useCalendar';
import DayStatus from './DayStatus';
import LoadingSpinner from '../common/LoadingSpinner';
import Legend, { CalendarLegendItems } from '../common/Legend';
import { BookingSlot } from '../../types';
import "react-datepicker/dist/react-datepicker.css";
import './Calendar.css';

// Регистрируем русскую локаль
registerLocale('ru', ru);

interface CalendarProps {
  selectedDate: Date | null;
  onChange: (date: Date | null) => void;
}

export default function Calendar({ selectedDate, onChange }: CalendarProps) {
  const { loading, availability, fetchMonthAvailability, initializeCurrentMonth, refreshCurrentMonth } = useCalendar();
  const today = startOfDay(new Date());

  // Memoized function for determining availability classes - prevents recalculation on every render
  const getAvailabilityClass = useCallback((date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const dayAvailability = availability[dateStr];
    const isPastDate = isBefore(date, today);

    // Прошедшие даты - серые и неактивные
    if (isPastDate) {
      return 'bg-gray-100 text-gray-400 cursor-not-allowed';
    }

    // Если нет данных о доступности - обычные (белые)
    if (!dayAvailability) {
      return '';
    }

    // Определяем статус на основе количества доступных слотов
    const { available_slots = 0, total_slots = 12, booked_slots = 0 } = dayAvailability;
    
    if (available_slots === 0) {
      // Полностью занято - красные и неактивные
      return 'bg-red-100 text-red-800 cursor-not-allowed';
    } else if (booked_slots > 0) {
      // Частично занято - жёлтые
      return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
    } else {
      // Полностью доступно - зелёные
      return 'bg-green-100 text-green-800 hover:bg-green-200';
    }
  }, [availability, today]);

  // Memoized function for determining if date is selectable
  const isDateSelectable = useCallback((date: Date) => {
    const isPastDate = isBefore(date, today);
    if (isPastDate) return false;

    const dateStr = format(date, 'yyyy-MM-dd');
    const dayAvailability = availability[dateStr];
    
    // Если нет данных о доступности, разрешаем выбор (по умолчанию даты доступны)
    if (!dayAvailability) return true;
    
    // Проверяем наличие доступных слотов
    const { available_slots = 0 } = dayAvailability;
    return available_slots > 0;
  }, [availability, today]);

  // Обработчик изменения даты - теперь просто передаем дату, без дополнительной загрузки
  // TimeSlots компонент сам загрузит детали для выбранной даты
  const handleDateChange = useCallback(async (date: Date | null) => {
    onChange(date);
  }, [onChange]);

  // Обработчик смены месяца - загружаем весь месяц сразу
  const handleMonthChange = useCallback(async (date: Date) => {
    console.log('Month changed, loading month data for:', format(date, 'yyyy-MM'));
    await fetchMonthAvailability(date);
  }, [fetchMonthAvailability]);

  // Инициализация - загружаем текущий месяц одним запросом
  useEffect(() => {
    console.log('Calendar initializing, loading current month');
    initializeCurrentMonth();
    
    // Add event listener for booking creation to refresh calendar
    const handleBookingCreated = (event: CustomEvent) => {
      console.log('Booking created, refreshing calendar data:', event.detail);
      // Use the refresh function to force reload data
      refreshCurrentMonth();
    };
    
    window.addEventListener('bookingCreated', handleBookingCreated as EventListener);
    
    // Cleanup event listener
    return () => {
      window.removeEventListener('bookingCreated', handleBookingCreated as EventListener);
    };
  }, [initializeCurrentMonth, refreshCurrentMonth]);

  // Memoized render day contents to prevent unnecessary re-renders
  const renderDayContents = useCallback((day: number, date?: Date) => {
    if (!date) return day;
    
    const isPastDate = isBefore(date, today);
    const dateStr = format(date, 'yyyy-MM-dd');
    const dayAvailability = availability[dateStr];
    
    return (
      <DayStatus
        day={day}
        isAvailable={dayAvailability?.isAvailable}
        slots={dayAvailability?.slots}
        isPast={isPastDate}
      />
    );
  }, [availability, today]);

  return (
    <div className="calendar-container">
      <div className="calendar-wrapper relative flex justify-center">
        <DatePicker
          selected={selectedDate}
          onChange={handleDateChange}
          onMonthChange={handleMonthChange}
          dayClassName={getAvailabilityClass}
          filterDate={isDateSelectable}
          minDate={new Date()}
          inline
          locale="ru"
          calendarClassName="modern-calendar"
          renderDayContents={renderDayContents}
        />
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        )}
      </div>
      
      {/* Легенда календаря */}
      <Legend 
        items={CalendarLegendItems} 
        className="mt-4" 
        size="md"
      />
    </div>
  );
}