import { BookingSlot, DayAvailability } from '../../types';
import { formatLocalDate } from '../../utils/dateUtils';
import { getDayAvailability } from './availability';

/**
 * Получает доступные слоты для указанной даты.
 */
export async function getTimeSlots(date: string): Promise<BookingSlot[]> {
  // Directly return the slots from the availability function
  return (await getDayAvailability(date)).slots || [];
}

/**
 * Получает доступность для списка дат за последующие 30 дней
 */
export async function getMultiDayAvailability(startDate?: string): Promise<DayAvailability[]> {
  console.log(`[slots.ts] Getting multi-day availability, start date: ${startDate || 'today'}`);
  const today = startDate ? new Date(startDate) : new Date();
  const availabilityPromises: Promise<DayAvailability>[] = [];

  for (let i = 0; i < 30; i++) {
    const currentDate = new Date(today);
    currentDate.setDate(today.getDate() + i);
    const dateString = formatLocalDate(currentDate);
    
    availabilityPromises.push(
      getDayAvailability(dateString)
    );
  }

  return Promise.all(availabilityPromises);
}

/**
 * Проверяет, доступны ли выбранные слоты.
 */
export async function checkSlotsAvailability(date: string, times: string[]): Promise<boolean> {
  // Ensure the date is in the correct format
  const formattedDate = formatLocalDate(date);
  
  console.log(`[slots.ts] Checking slots availability for date: ${formattedDate}, times: ${times.join(', ')}`);
  const availableSlots = await getTimeSlots(formattedDate);

  // Проверяем, все ли выбранные слоты доступны
  return times.every(time => {
    const slot = availableSlots.find(slot => slot.startTime === time);
    return slot && slot.available;
  });
}

/**
 * Бронирует выбранные слоты.
 */
export async function bookSlots(date: string, times: string[]): Promise<void> {
  // Ensure the date is in the correct format
  const formattedDate = formatLocalDate(date);
  
  console.log(`[slots.ts] Booking slots for date: ${formattedDate}, times: ${times.join(', ')}`);
  // Note: Actual booking is handled through the booking API service, not here
  // This function is kept for compatibility but doesn't need to do anything
  // since bookings go through createBooking() service
}