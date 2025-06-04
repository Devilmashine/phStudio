import { 
  BookingSlot, 
  DateAvailabilityStatusType, 
  DayAvailability 
} from '../types/index';
import { fetchCalendarEvents } from '../services/calendar/api';
import { 
  formatLocalDate, 
  preserveLocalDateInUTC 
} from '../utils/dateUtils';

/**
 * Получает доступность на указанную дату.
 * @param date - Дата в формате YYYY-MM-DD.
 * @returns Объект с датой и статусом доступности.
 */
export async function getDayAvailability(date: string): Promise<DayAvailability> {
  // Ensure consistent date formatting
  const formattedDate = formatLocalDate(date);

  // Create UTC timestamps that preserve the local date
  const timeMinIso = preserveLocalDateInUTC(formattedDate + 'T00:00:00').toISOString();
  const timeMaxIso = preserveLocalDateInUTC(formattedDate + 'T23:59:59').toISOString();

  try {
    const events = await fetchCalendarEvents(timeMinIso, timeMaxIso);

    // Подсчет количества занятых часов
    const bookedSlots = new Set<string>();
    events.forEach((event) => {
      const start = event.start.dateTime || event.start.date || timeMinIso;
      const end = event.end.dateTime || event.end.date || timeMaxIso;

      const startDate = new Date(start);
      const endDate = new Date(end);

      // Ensure we're only counting hours within the specified date
      for (let time = new Date(startDate); time < endDate; time.setHours(time.getHours() + 1)) {
        // Only add hours between 9 and 20
        const hour = time.getHours();
        if (hour >= 9 && hour <= 20) {
          bookedSlots.add(`${hour.toString().padStart(2, '0')}:00`);
        }
      }
    });

    // Генерация слотов для дня
    const slots: BookingSlot[] = [];

    for (let hour = 9; hour <= 20; hour++) {
      const time = `${hour.toString().padStart(2, '0')}:00`;
      const nextHour = `${(hour + 1).toString().padStart(2, '0')}:00`;
      
      slots.push({
        date: formattedDate,
        startTime: time,
        endTime: nextHour,
        available: !bookedSlots.has(time),
        bookedPercentage: bookedSlots.has(time) ? 100 : 0
      });
    }

    // Определение статуса дня
    let status: DateAvailabilityStatusType = DateAvailabilityStatusType.UNKNOWN;
    if (slots.every(slot => !slot.available)) {
      status = DateAvailabilityStatusType.FULLY_BOOKED;
    } else if (slots.some(slot => !slot.available)) {
      status = DateAvailabilityStatusType.PARTIALLY_BOOKED;
    } else {
      status = DateAvailabilityStatusType.AVAILABLE;
    }

    return { 
      date: formattedDate, 
      isAvailable: status !== DateAvailabilityStatusType.FULLY_BOOKED,
      status,
      slots 
    };
  } catch (error) {
    console.error('Error fetching real calendar events in getDayAvailability:', error);
    return { 
      date: formattedDate, 
      isAvailable: false,
      status: DateAvailabilityStatusType.UNKNOWN,
      slots: [] as BookingSlot[] 
    };
  }
}

/**
 * Получает временные слоты для указанной даты.
 * @param date - Дата в формате YYYY-MM-DD.
 * @returns Объект с датой и списком слотов времени.
 */
export async function getTimeSlots(date: string): Promise<BookingSlot> {
  // Ensure consistent date formatting
  const formattedDate = formatLocalDate(date);

  // Create UTC timestamps that preserve the local date
  const timeMinIso = preserveLocalDateInUTC(formattedDate + 'T00:00:00').toISOString();
  const timeMaxIso = preserveLocalDateInUTC(formattedDate + 'T23:59:59').toISOString();

  try {
    const events = await fetchCalendarEvents(timeMinIso, timeMaxIso);
    const bookedSlots = new Set();

    events.forEach((event) => {
      const startDateTime = event.start.dateTime || event.start.date;
      const endDateTime = event.end.dateTime || event.end.date;
      
      if (!startDateTime || !endDateTime) {
        return;
      }

      const start = new Date(startDateTime);
      const end = new Date(endDateTime);

      for (let time = start; time < end; time.setHours(time.getHours() + 1)) {
        bookedSlots.add(`${time.getHours().toString().padStart(2, '0')}:00`);
      }
    });

    for (let hour = 9; hour <= 20; hour++) {
      const time = `${hour.toString().padStart(2, '0')}:00`;
      const endTime = `${(hour + 1).toString().padStart(2, '0')}:00`;
      return {
        date: formattedDate,
        startTime: time,
        endTime: endTime,
        available: !bookedSlots.has(time),
        bookedPercentage: bookedSlots.has(time) ? 100 : 0
      };
    }

    throw new Error('No available time slots found');
  } catch (error) {
    console.error('Error fetching time slots:', error);
    // Return a default slot in case of error
    return {
      date: formattedDate,
      startTime: '09:00',
      endTime: '10:00',
      available: false,
      bookedPercentage: 100
    };
  }
}