import { getAvailableSlots } from '../../data/availability';
import { AvailabilityState } from '../../types/index';


interface AvailableSlot {
  time: string;
  state?: AvailabilityState;
  bookedPercentage?: number;
  isBookable: boolean;
  events?: { start: string, end: string }[];
}

async function getMappedAvailableSlots(date: string): Promise<AvailableSlot[]> {
  const { slots } = await getAvailableSlots(date);
  return slots.map(s => ({
    time: s.startTime,
    state: s.state,
    bookedPercentage: s.bookedPercentage,
    isBookable: s.available
  }));
}

/**
 * Получает доступные слоты для указанной даты.
 */
export async function getBookingSlots(date: string): Promise<AvailableSlot[]> {
  try {
    return await getMappedAvailableSlots(date);
  } catch (error) {
    console.error('Error fetching booking slots:', error);
    throw new Error('Не удалось загрузить доступные слоты. Пожалуйста, попробуйте позже.');
  }
}

export async function checkAvailability(date: string, slots: string[]): Promise<boolean> {
  try {
    // Fetch available slots for the date
    const availableSlots = await getMappedAvailableSlots(date);

    // Check if all requested slots are available and bookable
    return slots.every(slot => {
      const matchingSlot = availableSlots.find(
        (availableSlot: AvailableSlot) => availableSlot.time === slot
      );
      
      // Only allow bookable slots
      return matchingSlot && matchingSlot.isBookable;
    });
  } catch (error) {
    console.error('Error checking availability:', error);
    return false;
  }
}

// Detailed availability information for frontend
export async function getDetailedAvailability(date: string): Promise<{
  time: string, 
  isBookable: boolean, 
  bookedPercentage?: number,
  events?: { start: string, end: string }[]
}[]> {
  try {
    const availableSlots = await getMappedAvailableSlots(date);

    return availableSlots.map(slot => ({
      time: slot.time,
      isBookable: slot.isBookable,
      bookedPercentage: slot.bookedPercentage,
      events: slot.events
    }));
  } catch (error) {
    console.error('Error fetching detailed availability:', error);
    return [];
  }
}

// Backward compatibility function for components expecting isBooked
export async function getBookingAvailability(date: string): Promise<{time: string, isBooked: boolean}[]> {
  try {
    const availableSlots = await getMappedAvailableSlots(date);

    return availableSlots.map(slot => ({
      time: slot.time,
      isBooked: !slot.isBookable
    }));
  } catch (error) {
    console.error('Error fetching booking availability:', error);
    return [];
  }
}