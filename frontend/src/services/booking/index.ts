import { BookingData } from '../../types';
import { getDayAvailability } from '../calendar/availability';
import { calendarService } from '../calendar.service';
import { telegramNotificationService } from '../telegram/sendBooking';
import { createBookingApi, CreateBookingRequest } from './api';

// Diagnostic logging for booking module
console.warn('🚨 BOOKING MODULE LOADED 🚨');
console.log('📦 Booking Module Import Details:', {
  telegramImportStatus: 'Imported',
  telegramSendFunctionPresent: true,
  
  // Additional runtime checks
  nodeEnv: process.env.NODE_ENV,
  viteMode: (import.meta as any).env?.MODE || 'unknown',
  
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
    const dayAvailability = await getDayAvailability(date);
    const { slots } = dayAvailability;
    const bookedSlots = new Set<string>();

    slots.forEach(slot => {
      if (!slot.available) {
        bookedSlots.add(slot.startTime);
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

  // Validate that all times are full hours
  const invalidTimes = bookingData.times.filter(time => {
    const [hours, minutes] = time.split(':').map(Number);
    return isNaN(hours) || isNaN(minutes) || minutes !== 0;
  });

  if (invalidTimes.length > 0) {
    throw new Error('Все временные слоты должны быть целыми часами (например, 10:00, 11:00)');
  }

  // Sort times and create a single booking that spans all selected slots
  const sortedTimes = [...bookingData.times].sort();
  const startTime = sortedTimes[0];
  // Calculate end time correctly - it should be the hour after the last selected slot
  const lastSlotHour = parseInt(sortedTimes[sortedTimes.length - 1].split(':')[0]);
  const endTime = `${lastSlotHour + 1}:00`;

  // Prepare booking data for API with proper timezone handling
  // Use the date and time directly without timezone conversion to avoid half-hour offsets
  const apiBookingData: CreateBookingRequest = {
    date: bookingData.date,
    start_time: `${bookingData.date}T${startTime}:00+03:00`, // Moscow timezone
    end_time: `${bookingData.date}T${endTime}:00+03:00`, // Moscow timezone
    total_price: bookingData.totalPrice,
    client_name: bookingData.name,
    client_phone: bookingData.phone,
  };

  console.warn('🚨 SENDING BOOKING TO BACKEND API 🚨');
  
  try {
    // Send booking to backend API
    const apiResponse = await createBookingApi(apiBookingData);
    
    // Only proceed with local booking and calendar event if backend API call succeeds
    console.warn('✅ BACKEND BOOKING CREATED SUCCESSFULLY');
    console.log('📋 Backend Booking Response:', apiResponse);
    
    // Prepare booking data for local storage and calendar
    const bookingId = generateBookingId();
    const booking: BookingData = {
      id: bookingId,
      ...bookingData,
      status: 'pending'
    };

    console.warn('🚨 BEFORE CALENDAR EVENT CREATION 🚨');
    
    // Create calendar event that spans all selected slots
    const calendarEvent = await calendarService.createEvent({
      summary: `Бронирование для ${bookingData.name}`,
      description: `Бронирование ${bookingData.name}, Телефон: ${bookingData.phone}`,
      start: {
        dateTime: `${bookingData.date}T${startTime}:00`,
        timeZone: 'Europe/Moscow'
      },
      end: {
        dateTime: `${bookingData.date}T${endTime}:00`,
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
  } catch (error) {
    console.error('Error creating booking via API:', error);
    throw error;
  }
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