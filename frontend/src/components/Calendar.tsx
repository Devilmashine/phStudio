import React from 'react';
import DatePicker from 'react-datepicker';
import { format } from 'date-fns';
import { getDayAvailability } from '../data/availability';
import "react-datepicker/dist/react-datepicker.css";

interface CalendarProps {
  selectedDate: Date | null;
  onChange: (date: Date | null) => void;
}

export default function Calendar({ selectedDate, onChange }: CalendarProps) {
  const [loading, setLoading] = React.useState(false);
  const [availability, setAvailability] = React.useState<Record<string, boolean>>({});

  const getAvailabilityClass = (date: Date) => {
    if (loading) return '';

    const dateStr = format(date, 'yyyy-MM-dd');
    const isAvailable = availability[dateStr];

    if (isAvailable === undefined) return '';
    return isAvailable 
      ? 'bg-green-100 text-green-800 hover:bg-green-200'
      : 'bg-red-100 text-red-800 hover:bg-red-200';
  };

  const handleDateChange = async (date: Date | null) => {
    if (date) {
      setLoading(true);
      try {
        const dateStr = format(date, 'yyyy-MM-dd');
        const dayAvailability = await getDayAvailability(dateStr);
        setAvailability((prev) => ({
          ...prev,
          [dateStr]: dayAvailability.isAvailable,
        }));
      } catch (error) {
        console.error('Error fetching availability:', error);
        setAvailability((prev) => ({
          ...prev,
          [format(date, 'yyyy-MM-dd')]: true, // В случае ошибки считаем день доступным
        }));
      } finally {
        setLoading(false);
      }
    }
    onChange(date);
  };

  return (
    <div className="calendar-wrapper">
      <DatePicker
        selected={selectedDate}
        onChange={handleDateChange}
        inline
        minDate={new Date()}
        dayClassName={getAvailabilityClass}
      />
      <div className="flex justify-center space-x-4 mt-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-green-100 mr-2"></div>
          <span>Свободно</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-red-100 mr-2"></div>
          <span>Занято</span>
        </div>
      </div>
    </div>
  );
}