import { 
  DayAvailability, 
  AvailabilityState as DateAvailabilityStatusType,
  BookingSlot
} from '../../types/index';
import { fetchDayDetails } from './api';
import { formatLocalDate } from '../../utils/dateUtils';

export async function getDayAvailability(date: string): Promise<DayAvailability> {
  // Ensure consistent date formatting
  const formattedDate = formatLocalDate(date);
  console.log(`🚀 [getDayAvailability] Input date: ${date}`);
  console.log(`🚀 [getDayAvailability] Formatted date: ${formattedDate}`);
  
  try {
    // Use real API instead of mock
    console.log(`🌐 [getDayAvailability] Calling fetchDayDetails for: ${formattedDate}`);
    const dayDetails = await fetchDayDetails(formattedDate);
    console.log(`✅ [getDayAvailability] API response for ${formattedDate}:`, dayDetails);
    
    // Convert API response to BookingSlot format
    const slots: BookingSlot[] = dayDetails.slots.map(slot => ({
      date: formattedDate,
      startTime: slot.time,
      endTime: `${(parseInt(slot.time.split(':')[0]) + 1).toString().padStart(2, '0')}:00`,
      available: slot.available,
      bookedPercentage: slot.available ? 0 : 100,
      state: slot.available ? DateAvailabilityStatusType.AVAILABLE : DateAvailabilityStatusType.FULLY_BOOKED
    }));
    
    // Calculate availability status
    const availableSlots = slots.filter(slot => slot.available).length;
    const totalSlots = slots.length;
    
    let status: DateAvailabilityStatusType;
    if (availableSlots === 0) {
      status = DateAvailabilityStatusType.FULLY_BOOKED;
    } else if (availableSlots < totalSlots) {
      status = DateAvailabilityStatusType.PARTIALLY_BOOKED;
    } else {
      status = DateAvailabilityStatusType.AVAILABLE;
    }
    
    return {
      date: formattedDate,
      isAvailable: availableSlots > 0,
      status,
      slots
    };
  } catch (error) {
    console.error('Error fetching day availability from API:', error);
    
    // Re-throw error instead of providing fallback data
    // This ensures components handle API failures properly
    throw new Error(`Failed to fetch availability for ${formattedDate}: ${error}`);
  }
}