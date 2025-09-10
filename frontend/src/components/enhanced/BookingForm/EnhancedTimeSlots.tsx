/**
 * Enhanced Time Slots Component
 * Улучшенный компонент выбора временных слотов с проверкой доступности
 */

import React, { useState, useEffect } from 'react';
import { SpaceType } from '../../../stores/types';
import { enhancedBookingApi } from '../../../services/api/enhancedBookingApi';
import LoadingSpinner from '../../common/LoadingSpinner';

interface TimeSlot {
  time: string;
  available: boolean;
  price: number;
  bookingId?: number;
  clientName?: string;
}

interface EnhancedTimeSlotsProps {
  date: Date;
  selectedSlots: string[];
  onSlotsChange: (slots: string[]) => void;
  availableSlots: string[];
  spaceType: SpaceType;
}

export const EnhancedTimeSlots: React.FC<EnhancedTimeSlotsProps> = ({
  date,
  selectedSlots,
  onSlotsChange,
  spaceType
}) => {
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate time slots for the day (9 AM to 11 PM)
  const generateTimeSlots = (): string[] => {
    const slots: string[] = [];
    for (let hour = 9; hour <= 23; hour++) {
      slots.push(`${hour.toString().padStart(2, '0')}:00`);
    }
    return slots;
  };

  // Fetch availability for the selected date
  useEffect(() => {
    const fetchAvailability = async () => {
      setLoading(true);
      setError(null);

      try {
        const dateString = date.toISOString().split('T')[0];
        const bookings = await enhancedBookingApi.getBookingsForDate(dateString);
        
        const allSlots = generateTimeSlots();
        const slotsWithAvailability: TimeSlot[] = allSlots.map(time => {
          // Check if this time slot conflicts with any existing booking
          const conflictingBooking = bookings.find(booking => {
            const bookingStart = new Date(booking.start_time);
            const bookingEnd = new Date(booking.end_time);
            const slotTime = new Date(`${dateString}T${time}:00`);
            const slotEndTime = new Date(slotTime.getTime() + 60 * 60 * 1000); // 1 hour later
            
            return (
              (slotTime >= bookingStart && slotTime < bookingEnd) ||
              (slotEndTime > bookingStart && slotEndTime <= bookingEnd) ||
              (slotTime <= bookingStart && slotEndTime >= bookingEnd)
            ) && booking.space_type === spaceType;
          });

          // Calculate price based on time and space type
          const hour = parseInt(time.split(':')[0]);
          let basePrice = 2000; // Base price per hour
          
          // Peak hours (evening) cost more
          if (hour >= 18 && hour <= 21) {
            basePrice = 2500;
          }
          
          // Space type multiplier
          const spaceMultiplier = {
            [SpaceType.MAIN_STUDIO]: 1.0,
            [SpaceType.SMALL_STUDIO]: 0.8,
            [SpaceType.OUTDOOR_AREA]: 1.2,
          };

          const finalPrice = basePrice * spaceMultiplier[spaceType];

          return {
            time,
            available: !conflictingBooking,
            price: finalPrice,
            bookingId: conflictingBooking?.id,
            clientName: conflictingBooking?.client_name,
          };
        });

        setTimeSlots(slotsWithAvailability);
      } catch (err: any) {
        setError(err.message || 'Ошибка загрузки доступных слотов');
      } finally {
        setLoading(false);
      }
    };

    fetchAvailability();
  }, [date, spaceType]);

  const handleSlotClick = (time: string, available: boolean) => {
    if (!available) return;

    const currentIndex = selectedSlots.indexOf(time);
    let newSelectedSlots: string[];

    if (currentIndex === -1) {
      // Add slot
      newSelectedSlots = [...selectedSlots, time].sort();
    } else {
      // Remove slot
      newSelectedSlots = selectedSlots.filter(slot => slot !== time);
    }

    // Validate that selected slots are consecutive
    if (newSelectedSlots.length > 1) {
      const sortedSlots = newSelectedSlots.sort();
      const isConsecutive = sortedSlots.every((slot, index) => {
        if (index === 0) return true;
        const currentHour = parseInt(slot.split(':')[0]);
        const previousHour = parseInt(sortedSlots[index - 1].split(':')[0]);
        return currentHour === previousHour + 1;
      });

      if (!isConsecutive) {
        // If not consecutive, start a new selection from this slot
        newSelectedSlots = [time];
      }
    }

    onSlotsChange(newSelectedSlots);
  };

  const getSlotClasses = (slot: TimeSlot): string => {
    const baseClasses = "relative p-3 rounded-lg border-2 transition-all duration-200 cursor-pointer text-center";
    
    if (!slot.available) {
      return `${baseClasses} bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed`;
    }
    
    const isSelected = selectedSlots.includes(slot.time);
    
    if (isSelected) {
      return `${baseClasses} bg-indigo-600 border-indigo-600 text-white hover:bg-indigo-700 hover:border-indigo-700`;
    }
    
    return `${baseClasses} bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20`;
  };

  const formatTime = (time: string): string => {
    const [hour] = time.split(':');
    const hourNum = parseInt(hour);
    return `${hourNum}:00`;
  };

  const formatPrice = (price: number): string => {
    return `${price.toLocaleString('ru-RU')} ₽`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner className="w-8 h-8" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Загрузка слотов...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-700 dark:text-red-300">{error}</p>
      </div>
    );
  }

  const totalPrice = selectedSlots.reduce((sum, time) => {
    const slot = timeSlots.find(s => s.time === time);
    return sum + (slot?.price || 0);
  }, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
          Доступное время
        </h4>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {date.toLocaleDateString('ru-RU', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      {/* Time slots grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {timeSlots.map((slot) => (
          <button
            key={slot.time}
            onClick={() => handleSlotClick(slot.time, slot.available)}
            className={getSlotClasses(slot)}
            disabled={!slot.available}
            title={
              slot.available 
                ? `${formatTime(slot.time)} - ${formatPrice(slot.price)}`
                : `Занято: ${slot.clientName}`
            }
          >
            <div className="text-sm font-medium">
              {formatTime(slot.time)}
            </div>
            
            {slot.available ? (
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {formatPrice(slot.price)}
              </div>
            ) : (
              <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                Занято
              </div>
            )}
            
            {/* Peak hours indicator */}
            {slot.available && parseInt(slot.time.split(':')[0]) >= 18 && parseInt(slot.time.split(':')[0]) <= 21 && (
              <div className="absolute top-1 right-1">
                <div className="w-2 h-2 bg-yellow-400 rounded-full" title="Пиковые часы" />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Selection summary */}
      {selectedSlots.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                Выбрано: {selectedSlots.length} час{selectedSlots.length > 1 ? (selectedSlots.length > 4 ? 'ов' : 'а') : ''}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {selectedSlots.sort().join(' - ')}
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                {formatPrice(totalPrice)}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {formatPrice(Math.round(totalPrice / selectedSlots.length))}/час
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
        <p>• Выберите один или несколько последовательных часов</p>
        <p>• Пиковые часы (18:00-21:00) стоят дороже</p>
        <p>• Минимальное время бронирования - 1 час</p>
      </div>
    </div>
  );
};

export default EnhancedTimeSlots;
