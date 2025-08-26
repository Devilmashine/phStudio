import React from 'react';
import { getTimeSlots } from '../services/calendar/slots';
import LoadingSpinner from './common/LoadingSpinner';
import { BookingSlot } from '../types';
import { isSameDay, isAfter, parseISO } from 'date-fns';

interface TimeSlotsProps {
  date: Date;
  selectedTimes: string[];
  onSelectTime: (time: string) => void;
}

export default function TimeSlots({ date, selectedTimes, onSelectTime }: TimeSlotsProps) {
  const [slots, setSlots] = React.useState<BookingSlot[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Helper function to check if a time slot is in the past (for current day only)
  const isTimeSlotInPast = React.useCallback((timeSlot: string, slotDate: Date): boolean => {
    const now = new Date();
    
    // Only apply past time logic for the current day
    if (!isSameDay(slotDate, now)) {
      return false;
    }

    // Parse the time slot (format: "HH:mm")
    const [hours, minutes = 0] = timeSlot.split(':').map(Number);
    
    // Create a date object for the slot time on the selected date
    const slotDateTime = new Date(slotDate);
    slotDateTime.setHours(hours, minutes, 0, 0);
    
    // Check if slot time has passed
    return isAfter(now, slotDateTime);
  }, []);

  React.useEffect(() => {
    const fetchSlots = async () => {
      try {
        setLoading(true);
        setError(null);

        // Convert date to YYYY-MM-DD format without timezone conversion
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        
        console.log(`🗓️ [TimeSlots] Date prop received:`, date);
        console.log(`🗓️ [TimeSlots] Converted to dateStr:`, dateStr);

        // Получаем доступные слоты
        const availableSlots = await getTimeSlots(dateStr);
        console.log(`🎯 [TimeSlots] Received slots for ${dateStr}:`, availableSlots);
        setSlots(availableSlots);
      } catch (err) {
        console.error('Error fetching slots:', err);
        setError('Не удалось загрузить доступные слоты. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    console.log(`🔄 [TimeSlots] useEffect triggered, date changed to:`, date);
    fetchSlots();
    
    // Add event listener for booking creation to refresh slots
    const handleBookingCreated = (event: CustomEvent) => {
      // Use the same local date conversion to avoid timezone issues
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const currentDateStr = `${year}-${month}-${day}`;
      // Only refresh if the booking is for the currently displayed date
      if (event.detail?.date === currentDateStr) {
        console.log('Booking created for current date, refreshing slots');
        fetchSlots();
      }
    };
    
    window.addEventListener('bookingCreated', handleBookingCreated as EventListener);
    
    // Cleanup event listener
    return () => {
      window.removeEventListener('bookingCreated', handleBookingCreated as EventListener);
    };
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
        const isPastSlot = isTimeSlotInPast(slot.startTime, date);
        const isDisabled = !slot.available || isPastSlot;
        
        return (
          <button
            key={slot.startTime}
            onClick={() => !isDisabled && onSelectTime(slot.startTime)}
            disabled={isDisabled}
            className={`
              p-3 rounded-lg text-center transition-colors relative
              ${
                isDisabled 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                  : isSelected 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-white border border-gray-300 hover:bg-gray-50'
              }
            `}
            title={
              isPastSlot 
                ? 'Время уже прошло' 
                : !slot.available 
                ? 'Время занято' 
                : 'Выберите это время'
            }
          >
            {slot.startTime}
            {isPastSlot && (
              <span className="absolute top-1 right-1 text-xs text-gray-500">
                {/* Removed ⏰ emoji */}
              </span>
            )}
            {!slot.available && !isPastSlot && (
              <span className="absolute top-1 right-1 text-xs text-red-500">
                {/* Removed ❌ emoji */}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}