import { 
  fetchCalendarEvents,
  createCalendarEvent
} from './api';
import { 
  BookingSlot, 
  AvailabilityState as DateAvailabilityStatusType
} from '../../types/index';

export const mockAvailability = {
  getDayAvailability: async (date: string): Promise<{
    date: string;
    isAvailable: boolean;
    status: DateAvailabilityStatusType;
    slots: BookingSlot[];
  }> => {
    // Manually parse the date components and add one day
    const [year, month, day] = date.split('-').map(Number);
    
    // Create a date object and add one day
    const adjustedDate = new Date(Date.UTC(year, month - 1, day + 1));
    
    const formattedYear = adjustedDate.getUTCFullYear();
    const formattedMonth = (adjustedDate.getUTCMonth() + 1).toString().padStart(2, '0');
    const formattedDay = adjustedDate.getUTCDate().toString().padStart(2, '0');
    const formattedDate = `${formattedYear}-${formattedMonth}-${formattedDay}`;
    
    // Create timestamps for the entire day
    const timeMin = new Date(`${formattedDate}T00:00:00.000Z`);
    const timeMax = new Date(`${formattedDate}T23:59:59.000Z`);

    const timeMinIso = timeMin.toISOString();
    const timeMaxIso = timeMax.toISOString();

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
        const timeSlot = `${hour.toString().padStart(2, '0')}:00`;
        slots.push({
          date: formattedDate,
          startTime: timeSlot,
          endTime: `${(hour + 1).toString().padStart(2, '0')}:00`,
          available: !bookedSlots.has(timeSlot),
          bookedPercentage: bookedSlots.has(timeSlot) ? 100 : 0,
        });
      }

      return {
        date: formattedDate,
        isAvailable: slots.some(slot => slot.available),
        status: slots.every(slot => !slot.available) 
          ? DateAvailabilityStatusType.FULLY_BOOKED 
          : (slots.some(slot => !slot.available) 
            ? DateAvailabilityStatusType.PARTIALLY_BOOKED 
            : DateAvailabilityStatusType.AVAILABLE),
        slots,
      };
    } catch (error) {
      console.error('Error fetching events:', error);
      throw error;
    }
  },
  
  bookSlots: async (date: string, times: string[]): Promise<void> => {
    try {
      // Explicitly reference parameters to prevent unused warnings
      void date;
      void times;
      return Promise.resolve();
    } catch (error) {
      console.error('Error booking slots:', error);
      throw error;
    }
  },

  createBookingEvent: async (bookingData: {
    date: string;
    startTime: string;
    name: string;
    phone: string;
    totalPrice: number;
    peopleCount?: number;
    times?: string[];
  }): Promise<{ id: string }> => {
    // Get the current date in the local timezone
    const localTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // If no times provided, use startTime
    const times = bookingData.times || [bookingData.startTime];

    // Sort times
    const sortedTimes = times.sort();

    // Function to check if times are consecutive
    const areTimesConsecutive = (time1: string, time2: string) => {
      const [hour1, minute1] = time1.split(':').map(Number);
      const [hour2, minute2] = time2.split(':').map(Number);
      
      // Check if times are within 1 hour of each other
      return (hour2 === hour1 + 1 && minute1 === minute2) || 
             (hour2 === hour1 && minute2 === minute1 + 60);
    };

    // Group consecutive time slots
    const timeGroups: string[][] = [];
    let currentGroup: string[] = [sortedTimes[0]];

    for (let i = 1; i < sortedTimes.length; i++) {
      if (areTimesConsecutive(currentGroup[currentGroup.length - 1], sortedTimes[i])) {
        currentGroup.push(sortedTimes[i]);
      } else {
        timeGroups.push(currentGroup);
        currentGroup = [sortedTimes[i]];
      }
    }
    timeGroups.push(currentGroup);

    // Create events for each group
    const events = await Promise.all(timeGroups.map(async (group) => {
      // Find the first time in the group
      const startTime = group[0];

      // Calculate the end time by adding the number of slots to the first slot's hour
      const [startHour] = startTime.split(':').map(Number);
      const endHour = startHour + group.length;
      const formattedEndTime = `${endHour.toString().padStart(2, '0')}:00`;

      const calendarEvent = {
        kind: 'calendar#event',
        summary: `Бронирование для ${bookingData.name}`,
        description: `Бронирование ${bookingData.name}, Телефон: ${bookingData.phone}`,
        start: { 
          dateTime: `${bookingData.date}T${startTime}:00`,
          timeZone: localTimezone
        },
        end: { 
          dateTime: `${bookingData.date}T${formattedEndTime}:00`,
          timeZone: localTimezone
        },
        reminders: {
          useDefault: false,
          overrides: []
        },
        colorId: '7',
        status: 'confirmed'
      };

      return createCalendarEvent({
        ...calendarEvent,
        phone: bookingData.phone || '',
        total_price: bookingData.totalPrice,
        people_count: bookingData.peopleCount || 1
      });
    }));

    // Return the IDs of created events
    return { 
      id: events.map(event => event.id || `mock_event_${Date.now()}`).join(',') 
    };
  },
};