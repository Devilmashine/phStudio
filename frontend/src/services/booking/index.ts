import { BookingData } from '../../types';
import { getAvailableSlots } from '../google/calendar';
import { calendarService } from '../calendar.service';
import { telegramNotificationService } from '../telegram/sendBooking';

// Diagnostic logging for booking module
console.warn('🚨 BOOKING MODULE LOADED 🚨');
console.log('📦 Booking Module Import Details:', {
  telegramImportStatus: 'Imported',
  telegramSendFunctionPresent: true,
  
  // Additional runtime checks
  nodeEnv: process.env.NODE_ENV,
  viteMode: (import.meta.env as any)?.MODE,
  
  // Detailed environment variable logging
  telegramEnvVars: Object.keys(process.env)
    .filter(key => key.includes('TELEGRAM') || key.includes('VITE_TELEGRAM'))
    .reduce((acc, key) => {
      acc[key] = process.env[key] ? '✅ PRESENT (masked)' : '❌ MISSING';
      return acc;
    }, {} as Record<string, string>)
});

// Simple in-memory store for bookings (in production, this should be a database)
const bookingsStore = new Map<string, BookingData>();

/**
 * Generates a unique booking ID
 */
function generateBookingId(): string {
  return `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Retrieves a booking by its ID
 */
export function getBookingById(id: string): BookingData | undefined {
  return bookingsStore.get(id);
}

/**
 * Проверяет доступность слотов для указанной даты.
 */
export async function checkAvailability(date: string): Promise<Set<string>> {
  try {
    const slots = await getAvailableSlots(date);
    const bookedSlots = new Set<string>();

    slots.forEach(slot => {
      if (!slot.isBookable) {
        bookedSlots.add(slot.time);
      }
    });

    return bookedSlots;
  } catch (error) {
    console.error('Error checking availability:', error);
    throw new Error('Не удалось проверить доступность. Пожалуйста, попробуйте позже.');
  }
}

interface BookingRequest {
  date: string;
  times: string[];
  name: string;
  phone: string;
  totalPrice: number;
}

export async function createBooking(bookingData: BookingRequest): Promise<BookingData> {
  console.warn('🚨 CREATE BOOKING STARTED 🚨');
  console.log('📋 Booking Request Details:', {
    date: bookingData.date,
    times: bookingData.times,
    name: bookingData.name,
    phone: bookingData.phone,
    totalPrice: bookingData.totalPrice
  });

  // Generate unique booking ID
  const bookingId = generateBookingId();

  // Prepare booking data
  const booking: BookingData = {
    id: bookingId,
    ...bookingData,
    status: 'pending'
  };

  console.warn('🚨 BEFORE CALENDAR EVENT CREATION 🚨');
  
  // Create calendar event
  const calendarEvent = await calendarService.createEvent({
    summary: `Бронирование для ${bookingData.name}`,
    description: `Бронирование ${bookingData.name}, Телефон: ${bookingData.phone}`,
    start: {
      dateTime: new Date(`${bookingData.date}T${bookingData.times[0]}:00`).toISOString(),
      timeZone: 'Europe/Moscow'
    },
    end: {
      dateTime: new Date(`${bookingData.date}T${parseInt(bookingData.times[0]) + 1}:00:00`).toISOString(),
      timeZone: 'Europe/Moscow'
    },
    colorId: '7',
    status: 'confirmed'
  });

  console.warn('🚨 CALENDAR EVENT CREATED 🚨');
  console.log('📅 Calendar Event Details:', {
    eventId: calendarEvent.id,
    htmlLink: calendarEvent.htmlLink
  });

  // Store booking in memory
  bookingsStore.set(bookingId, booking);

  console.warn('🚨 ATTEMPTING TELEGRAM NOTIFICATION 🚨');
  
  try {
    // Принудительная отправка Telegram-уведомления
    console.warn('🚨 FORCING TELEGRAM NOTIFICATION 🚨');
    const result = await telegramNotificationService.sendBookingNotification(booking);
    console.warn('✅ TELEGRAM NOTIFICATION RESULT', result);
  } catch (telegramError) {
    console.error('❌ TELEGRAM NOTIFICATION FAILED', telegramError);
  }

  console.warn('🚨 BOOKING CREATION COMPLETED 🚨');
  
  return booking;
}

export async function confirmBooking(bookingId: string | undefined): Promise<BookingData | undefined> {
  if (!bookingId) {
    console.error('❌ CONFIRM BOOKING FAILED: No booking ID provided');
    return undefined;
  }

  const booking = bookingsStore.get(bookingId);
  
  if (!booking) {
    console.error(`❌ CONFIRM BOOKING FAILED: No booking found with ID ${bookingId}`);
    return undefined;
  }

  // Update booking status
  booking.status = 'confirmed';
  bookingsStore.set(bookingId, booking);

  console.warn('✅ BOOKING CONFIRMED 🚨');
  console.log('📋 Confirmed Booking Details:', {
    id: booking.id,
    name: booking.name,
    date: booking.date,
    times: booking.times
  });

  // Обновляем событие в календаре
  await calendarService.updateEvent(booking.id || '', {
    summary: `Подтверждено: ${booking.name}`
  });

  return booking;
}

export async function rejectBooking(bookingId: string): Promise<void> {
  const booking = bookingsStore.get(bookingId);
  
  if (!booking) {
    throw new Error('Бронирование не найдено');
  }

  // Удаляем событие из календаря
  await calendarService.deleteEvent(bookingId);

  // Удаляем бронирование из памяти
  bookingsStore.delete(bookingId);
}