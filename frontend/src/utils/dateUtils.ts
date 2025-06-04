/**
 * Converts a date to a consistent YYYY-MM-DD format
 * @param date - Input date or date string
 * @returns Date string in YYYY-MM-DD format
 */
export function formatLocalDate(date: string | Date): string {
  // If already a string in YYYY-MM-DD format, return as-is
  if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return date;
  }

  // Create a new date object with explicit parsing
  let inputDate: Date;
  if (date instanceof Date) {
    inputDate = new Date(date.getTime());
  } else if (typeof date === 'string') {
    // Try parsing with explicit time to avoid timezone shifts
    inputDate = new Date(`${date}T12:00:00`);
  } else {
    inputDate = new Date();
  }
  
  // Log detailed parsing information
  console.log(`[formatLocalDate] Input: ${date}`);
  console.log(`[formatLocalDate] Parsed Date: ${inputDate}`);
  console.log(`[formatLocalDate] getFullYear(): ${inputDate.getFullYear()}`);
  console.log(`[formatLocalDate] getMonth(): ${inputDate.getMonth()}`);
  console.log(`[formatLocalDate] getDate(): ${inputDate.getDate()}`);
  console.log(`[formatLocalDate] getTimezoneOffset(): ${inputDate.getTimezoneOffset()}`);

  // Extract components directly
  const year = inputDate.getFullYear();
  const month = (inputDate.getMonth() + 1).toString().padStart(2, '0');
  const day = inputDate.getDate().toString().padStart(2, '0');
  
  // Return in YYYY-MM-DD format
  const formattedDate = `${year}-${month}-${day}`;
  console.log(`[formatLocalDate] Formatted Date: ${formattedDate}`);
  
  return formattedDate;
}

/**
 * Creates a Date object at the start of the day
 * @param date - Input date or date string
 * @returns Date object at the start of the day
 */
export function getStartOfDay(date: string | Date): Date {
  const inputDate = date instanceof Date 
    ? date 
    : new Date(date);
  
  return new Date(
    inputDate.getFullYear(), 
    inputDate.getMonth(), 
    inputDate.getDate(), 
    0, 0, 0, 0
  );
}

/**
 * Creates a Date object at the end of the day
 * @param date - Input date or date string
 * @returns Date object at the end of the day
 */
export function getEndOfDay(date: string | Date): Date {
  const inputDate = date instanceof Date 
    ? date 
    : new Date(date);
  
  return new Date(
    inputDate.getFullYear(), 
    inputDate.getMonth(), 
    inputDate.getDate(), 
    23, 59, 59, 999
  );
}

/**
 * Converts a date to the exact same date in UTC
 * @param date - Input date or date string
 * @returns Date object in UTC with the same local date
 */
export function preserveLocalDateInUTC(date: string | Date): Date {
  // Parse the input date as a local date
  const localDate = date instanceof Date 
    ? date 
    : new Date(date);
  
  // Create a UTC date with the same local date components
  return new Date(Date.UTC(
    localDate.getFullYear(),
    localDate.getMonth(),
    localDate.getDate(),
    0, 0, 0, 0
  ));
}
