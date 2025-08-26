import React from 'react';
import DatePicker from 'react-datepicker';
import { getDayAvailability } from '../../services/calendar/availability';
import { formatLocalDate } from '../../utils/dateUtils';
import { 
  AvailabilityState,
  DayAvailability 
} from '../../types/index';

interface DateSelectorProps {
  selectedDate: Date | null;
  onChange: (date: Date | null) => void;
}

const DateSelector = React.memo(({ selectedDate, onChange }: DateSelectorProps) => {
  const [availabilityClasses, setAvailabilityClasses] = React.useState<Record<string, string>>({});

  const getAvailabilityClass = async (date: Date) => {
    const dateStr = formatLocalDate(date);
    try {
      const availability: DayAvailability = await getDayAvailability(dateStr);
      
      if (!availability || !availability.status) return '';
      
      let className = '';
      switch (availability.status) {
        case AvailabilityState.AVAILABLE:
          className = 'bg-green-100 text-green-800 hover:bg-green-200';
          break;
        case AvailabilityState.PARTIALLY_BOOKED:
          className = 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
          break;
        case AvailabilityState.FULLY_BOOKED:
          className = 'bg-red-100 text-red-800 hover:bg-red-200';
          break;
      }
      
      setAvailabilityClasses(prev => ({
        ...prev,
        [dateStr]: className
      }));
      return className;
    } catch (error) {
      console.error('Error fetching availability for date:', dateStr, error);
      return '';
    }
  };

  React.useEffect(() => {
    const updateAvailability = async (date: Date) => {
      await getAvailabilityClass(date);
    };
    
    if (selectedDate) {
      updateAvailability(selectedDate);
    }
  }, [selectedDate]);

  const dayClassName = (date: Date) => {
    const dateStr = formatLocalDate(date);
    return availabilityClasses[dateStr] || '';
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700">
        Выберите дату
      </label>
      <DatePicker
        selected={selectedDate}
        onChange={onChange}
        inline
        minDate={new Date()}
        dayClassName={dayClassName}
      />
      <div className="flex justify-center space-x-4 mt-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-green-100 mr-2"></div>
          <span>Свободно</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-yellow-100 mr-2"></div>
          <span>Частично занято</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-red-100 mr-2"></div>
          <span>Занято</span>
        </div>
      </div>
    </div>
  );
});

export default DateSelector;