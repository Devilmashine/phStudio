import ical from 'ical-generator';
import { parse } from 'date-fns';
import { BookingData } from '../../types';
import { generateEventDescription } from './eventDescription';
import { groupConsecutiveSlots } from './timeSlots';

/**
 * Generates an iCal event for a booking
 * @param booking Booking data to generate event for
 * @returns iCal calendar object
 */
export const generateICalEvent = (booking: BookingData) => {
  const calendar = ical({ name: 'Бронирование фотостудии' });
  const timeGroups = groupConsecutiveSlots(booking.times);
  
  timeGroups.forEach(group => {
    const startTime = parse(group[0], 'HH:mm', new Date(booking.date));
    const endTime = parse(group[group.length - 1], 'HH:mm', new Date(booking.date));
    endTime.setHours(endTime.getHours() + 1); // Add an hour to end time
    
    calendar.createEvent({
      start: startTime,
      end: endTime,
      summary: 'Бронирование фотостудии',
      description: generateEventDescription(booking),
      location: 'Фотостудия Light',
      url: 'https://studio-light.ru', // Optional: add your studio's website
    });
  });
  
  return calendar;
};

/**
 * Creates a downloadable iCal file and returns its URL
 * @param booking Booking data to create calendar file for
 * @returns URL to download the calendar file
 */
export const createCalendarFile = (booking: BookingData): string => {
  const calendar = generateICalEvent(booking);
  const icalData = calendar.toString();
  const blob = new Blob([icalData], { type: 'text/calendar;charset=utf-8' });
  return URL.createObjectURL(blob);
};