import { useState, useCallback, useMemo } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { fetchMonthAvailability, fetchDayDetails, MonthAvailabilityResponse, DayDetailResponse } from '../services/calendar/api';
import { AvailabilityState, DayAvailability, BookingSlot } from '../types/index';

interface MonthData {
  year: number;
  month: number;
  availability: MonthAvailabilityResponse;
  loadedAt: number;
}

interface DayDetailsCache {
  [date: string]: {
    data: DayDetailResponse;
    loadedAt: number;
  };
}

export function useCalendar() {
  const [loading, setLoading] = useState(false);
  const [monthDataCache, setMonthDataCache] = useState<Record<string, MonthData>>({});
  const [dayDetailsCache, setDayDetailsCache] = useState<DayDetailsCache>({});
  const [currentMonth, setCurrentMonth] = useState<Date>(new Date());
  const [loadingMonths, setLoadingMonths] = useState<Set<string>>(new Set());

  // Memoized availability calculation - prevents unnecessary recalculations
  const availability = useMemo(() => {
    const monthKey = format(currentMonth, 'yyyy-MM');
    const monthData = monthDataCache[monthKey];
    
    if (!monthData) {
      return {};
    }

    const result: Record<string, DayAvailability> = {};
    
    // Convert month availability data to DayAvailability format
    Object.entries(monthData.availability).forEach(([date, slots]) => {
      const { available_slots, total_slots, booked_slots } = slots;
      
      let status: AvailabilityState;
      if (available_slots === 0) {
        status = AvailabilityState.FULLY_BOOKED;
      } else if (booked_slots > 0) {
        status = AvailabilityState.PARTIALLY_BOOKED;
      } else {
        status = AvailabilityState.AVAILABLE;
      }

      result[date] = {
        date,
        isAvailable: available_slots > 0,
        status,
        slots: [], // Will be populated when day is selected
        available_slots,
        total_slots,
        booked_slots
      };
    });

    return result;
  }, [monthDataCache, currentMonth]);

  // Bulk fetch month availability - single API call
  const fetchMonthAvailabilityData = useCallback(async (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const monthKey = format(date, 'yyyy-MM');

    // Check cache first (5 minute TTL)
    const cached = monthDataCache[monthKey];
    const now = Date.now();
    if (cached && (now - cached.loadedAt) < 5 * 60 * 1000) {
      console.log(`Using cached month data for ${monthKey}`);
      return;
    }

    // Prevent duplicate calls for the same month
    if (loadingMonths.has(monthKey)) {
      console.log(`Already loading month data for ${monthKey}, skipping duplicate call`);
      return;
    }

    setLoadingMonths(prev => new Set(prev).add(monthKey));
    setLoading(true);
    try {
      console.log(`Loading month availability for ${monthKey}`);
      const availabilityData = await fetchMonthAvailability(year, month);
      
      const monthData: MonthData = {
        year,
        month,
        availability: availabilityData,
        loadedAt: now
      };

      setMonthDataCache(prev => ({
        ...prev,
        [monthKey]: monthData
      }));
      
      console.log(`Month data loaded for ${monthKey}:`, monthData);
    } catch (error) {
      console.error('Error fetching month availability:', error);
    } finally {
      setLoading(false);
      setLoadingMonths(prev => {
        const newSet = new Set(prev);
        newSet.delete(monthKey);
        return newSet;
      });
    }
  }, [monthDataCache, loadingMonths]);

  // Fetch detailed day information only when needed
  const fetchDayAvailability = useCallback(async (date: Date): Promise<DayAvailability | null> => {
    const dateStr = format(date, 'yyyy-MM-dd');
    
    // Check cache first (1 minute TTL for day details)
    const cached = dayDetailsCache[dateStr];
    const now = Date.now();
    if (cached && (now - cached.loadedAt) < 60 * 1000) {
      console.log(`Using cached day details for ${dateStr}`);
      return convertDayDetailsToAvailability(cached.data);
    }

    try {
      console.log(`Loading day details for ${dateStr}`);
      const dayDetails = await fetchDayDetails(dateStr);
      
      // Cache the day details
      setDayDetailsCache(prev => ({
        ...prev,
        [dateStr]: {
          data: dayDetails,
          loadedAt: Date.now()
        }
      }));

      return convertDayDetailsToAvailability(dayDetails);
    } catch (error) {
      console.error('Error fetching day details:', error);
      return null;
    }
  }, [dayDetailsCache]);

  // Helper function to convert day details to DayAvailability
  const convertDayDetailsToAvailability = (dayDetails: DayDetailResponse): DayAvailability => {
    const slots: BookingSlot[] = dayDetails.slots.map(slot => ({
      date: dayDetails.date,
      startTime: slot.time,
      endTime: `${(parseInt(slot.time.split(':')[0]) + 1).toString().padStart(2, '0')}:00`,
      available: slot.available,
      bookedPercentage: slot.available ? 0 : 100,
      state: slot.available ? AvailabilityState.AVAILABLE : AvailabilityState.FULLY_BOOKED
    }));

    const availableSlots = slots.filter(slot => slot.available).length;
    const totalSlots = slots.length;
    
    let status: AvailabilityState;
    if (availableSlots === 0) {
      status = AvailabilityState.FULLY_BOOKED;
    } else if (availableSlots < totalSlots) {
      status = AvailabilityState.PARTIALLY_BOOKED;
    } else {
      status = AvailabilityState.AVAILABLE;
    }

    return {
      date: dayDetails.date,
      isAvailable: availableSlots > 0,
      status,
      slots
    };
  };

  // Handle month navigation - load new month data
  const handleMonthChange = useCallback(async (date: Date) => {
    setCurrentMonth(date);
    await fetchMonthAvailabilityData(date);
  }, [fetchMonthAvailabilityData]);

  // Legacy compatibility function
  const fetchAvailability = useCallback(async (date: Date) => {
    return await fetchDayAvailability(date);
  }, [fetchDayAvailability]);

  // Initialize current month on first load
  const initializeCurrentMonth = useCallback(() => {
    fetchMonthAvailabilityData(currentMonth);
  }, [fetchMonthAvailabilityData, currentMonth]);
  
  // Manual refresh function to force reload data
  const refreshCurrentMonth = useCallback(() => {
    console.log('Manually refreshing calendar data');
    // Clear cache and loading state, then reload
    setMonthDataCache({});
    setDayDetailsCache({});
    setLoadingMonths(new Set());
    fetchMonthAvailabilityData(currentMonth);
  }, [fetchMonthAvailabilityData, currentMonth]);

  return {
    loading,
    availability,
    fetchAvailability,
    fetchDayAvailability,
    fetchMonthAvailability: handleMonthChange,
    initializeCurrentMonth,
    refreshCurrentMonth,
    currentMonth
  };
}