/**
 * Enhanced Calendar Component
 * Улучшенный календарь с интеграцией backend API
 */

import React, { useState, useEffect } from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { enhancedBookingApi } from '../../../services/api/enhancedBookingApi';
import LoadingSpinner from '../../common/LoadingSpinner';

interface EnhancedCalendarProps {
  selectedDate: Date | null;
  onDateSelect: (date: Date) => void;
  minDate?: Date;
  maxDate?: Date;
  disabledDates?: Date[];
}

interface DayAvailability {
  date: string;
  available: boolean;
  bookingCount: number;
  maxBookings: number;
}

export const EnhancedCalendar: React.FC<EnhancedCalendarProps> = ({
  selectedDate,
  onDateSelect,
  minDate = new Date(),
  maxDate,
  disabledDates = []
}) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [availability, setAvailability] = useState<Record<string, DayAvailability>>({});
  const [loading, setLoading] = useState(false);

  // Fetch availability data for current month
  useEffect(() => {
    const fetchAvailability = async () => {
      setLoading(true);
      try {
        const startOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
        const endOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
        
        // TODO: Implement availability API endpoint
        // For now, we'll simulate the data
        const mockAvailability: Record<string, DayAvailability> = {};
        
        for (let d = new Date(startOfMonth); d <= endOfMonth; d.setDate(d.getDate() + 1)) {
          const dateString = d.toISOString().split('T')[0];
          const dayOfWeek = d.getDay();
          const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
          
          mockAvailability[dateString] = {
            date: dateString,
            available: !isWeekend && d >= minDate,
            bookingCount: Math.floor(Math.random() * 8),
            maxBookings: 8
          };
        }
        
        setAvailability(mockAvailability);
      } catch (error) {
        console.error('Failed to fetch availability:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAvailability();
  }, [currentMonth, minDate]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newMonth = new Date(currentMonth);
    if (direction === 'prev') {
      newMonth.setMonth(newMonth.getMonth() - 1);
    } else {
      newMonth.setMonth(newMonth.getMonth() + 1);
    }
    setCurrentMonth(newMonth);
  };

  const getDaysInMonth = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: (Date | null)[] = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    return days;
  };

  const isDateDisabled = (date: Date): boolean => {
    if (date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    if (disabledDates.some(disabledDate => 
      disabledDate.toDateString() === date.toDateString()
    )) return true;

    const dateString = date.toISOString().split('T')[0];
    const dayAvailability = availability[dateString];
    
    return !dayAvailability?.available;
  };

  const isDateSelected = (date: Date): boolean => {
    return selectedDate?.toDateString() === date.toDateString();
  };

  const getDateClasses = (date: Date): string => {
    const baseClasses = "w-10 h-10 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center justify-center relative";
    
    if (isDateDisabled(date)) {
      return `${baseClasses} text-gray-400 dark:text-gray-600 cursor-not-allowed`;
    }
    
    if (isDateSelected(date)) {
      return `${baseClasses} bg-indigo-600 text-white hover:bg-indigo-700`;
    }
    
    const dateString = date.toISOString().split('T')[0];
    const dayAvailability = availability[dateString];
    const isToday = date.toDateString() === new Date().toDateString();
    
    let classes = `${baseClasses} cursor-pointer `;
    
    if (isToday) {
      classes += "ring-2 ring-indigo-500 ";
    }
    
    if (dayAvailability) {
      const utilizationRate = dayAvailability.bookingCount / dayAvailability.maxBookings;
      
      if (utilizationRate >= 0.8) {
        classes += "bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300 dark:hover:bg-red-900/50";
      } else if (utilizationRate >= 0.5) {
        classes += "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:hover:bg-yellow-900/50";
      } else {
        classes += "bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-300 dark:hover:bg-green-900/50";
      }
    } else {
      classes += "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100";
    }
    
    return classes;
  };

  const getAvailabilityIndicator = (date: Date) => {
    const dateString = date.toISOString().split('T')[0];
    const dayAvailability = availability[dateString];
    
    if (!dayAvailability) return null;
    
    const utilizationRate = dayAvailability.bookingCount / dayAvailability.maxBookings;
    
    return (
      <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2">
        <div 
          className={`w-1 h-1 rounded-full ${
            utilizationRate >= 0.8 ? 'bg-red-500' :
            utilizationRate >= 0.5 ? 'bg-yellow-500' :
            'bg-green-500'
          }`}
        />
      </div>
    );
  };

  const days = getDaysInMonth();
  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];
  const dayNames = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigateMonth('prev')}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          disabled={loading}
        >
          <ChevronLeftIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
        
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h2>
        
        <button
          onClick={() => navigateMonth('next')}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          disabled={loading}
        >
          <ChevronRightIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-8">
          <LoadingSpinner className="w-6 h-6" />
        </div>
      )}

      {!loading && (
        <>
          {/* Day names */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {dayNames.map(day => (
              <div key={day} className="text-center text-sm font-medium text-gray-500 dark:text-gray-400 p-2">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-1">
            {days.map((date, index) => (
              <div key={index} className="flex justify-center">
                {date ? (
                  <button
                    onClick={() => !isDateDisabled(date) && onDateSelect(date)}
                    className={getDateClasses(date)}
                    disabled={isDateDisabled(date)}
                  >
                    {date.getDate()}
                    {getAvailabilityIndicator(date)}
                  </button>
                ) : (
                  <div className="w-10 h-10" />
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-green-500" />
            <span className="text-gray-600 dark:text-gray-400">Свободно</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-yellow-500" />
            <span className="text-gray-600 dark:text-gray-400">Занято частично</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-red-500" />
            <span className="text-gray-600 dark:text-gray-400">Почти занято</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedCalendar;
