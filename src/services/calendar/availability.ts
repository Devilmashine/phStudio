import { 
  DayAvailability, 
  DateAvailabilityStatusType 
} from '../../types/index';
import { mockAvailability } from './mock';
import { formatLocalDate } from '../../utils/dateUtils';

export async function getDayAvailability(date: string): Promise<DayAvailability> {
  // Ensure consistent date formatting
  const formattedDate = formatLocalDate(date);
  
  const response = await mockAvailability.getDayAvailability(formattedDate);
  
  return { 
    date: formattedDate, 
    isAvailable: response.status !== 'fully-booked',
    status: response.status === 'fully-booked' 
      ? DateAvailabilityStatusType.FULLY_BOOKED 
      : (response.status === 'partially-booked' 
        ? DateAvailabilityStatusType.PARTIALLY_BOOKED 
        : DateAvailabilityStatusType.AVAILABLE),
    slots: response.slots || [] 
  };
}