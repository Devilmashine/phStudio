export const formatDate = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const formatTime = (time: string): string => {
  return new Date(`2000-01-01T${time}`).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDateTime = (date: string, time: string): string => {
  return `${formatDate(date)} в ${formatTime(time)}`;
};

export const getTimeSlots = (start: string, end: string, interval: number = 30): string[] => {
  const slots: string[] = [];
  const [startHour, startMinute] = start.split(':').map(Number);
  const [endHour, endMinute] = end.split(':').map(Number);
  
  let currentHour = startHour;
  let currentMinute = startMinute;
  
  while (currentHour < endHour || (currentHour === endHour && currentMinute <= endMinute)) {
    slots.push(
      `${currentHour.toString().padStart(2, '0')}:${currentMinute.toString().padStart(2, '0')}`
    );
    
    currentMinute += interval;
    if (currentMinute >= 60) {
      currentHour++;
      currentMinute = 0;
    }
  }
  
  return slots;
};

export const isTimeSlotAvailable = (
  slot: string,
  bookings: Array<{ start_time: string; end_time: string }>
): boolean => {
  const [slotHour, slotMinute] = slot.split(':').map(Number);
  const slotTime = new Date(2000, 0, 1, slotHour, slotMinute);
  
  return !bookings.some(booking => {
    const [startHour, startMinute] = booking.start_time.split(':').map(Number);
    const [endHour, endMinute] = booking.end_time.split(':').map(Number);
    
    const startTime = new Date(2000, 0, 1, startHour, startMinute);
    const endTime = new Date(2000, 0, 1, endHour, endMinute);
    
    return slotTime >= startTime && slotTime < endTime;
  });
}; 