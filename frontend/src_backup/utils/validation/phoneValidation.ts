export const validatePhone = (phone: string): boolean => {
  // Remove all non-digit characters
  const digits = phone.replace(/\D/g, '');
  
  // Must be exactly 11 digits
  if (digits.length !== 11) return false;
  
  // Must start with 7
  if (digits[0] !== '7') return false;
  
  // Second digit must be 9 for mobile numbers
  if (digits[1] !== '9') return false;
  
  return true;
};

export const formatPhoneNumber = (value: string): string => {
  // If empty, always start with +7
  if (!value) return '+7';
  
  // Remove all non-digit characters
  let digits = value.replace(/\D/g, '');
  
  // If no digits entered yet, return +7
  if (digits.length === 0) return '+7';
  
  // Always ensure the number starts with 7
  if (digits[0] !== '7') {
    // If starts with 8, replace with 7
    if (digits[0] === '8') {
      digits = '7' + digits.slice(1);
    } else {
      // For any other number, append to existing 7
      digits = '7' + digits;
    }
  }
  
  // Limit to 11 digits
  digits = digits.slice(0, 11);
  
  // Format the number
  let formatted = '+7';
  if (digits.length > 1) formatted += ` (${digits.slice(1, 4)}`;
  if (digits.length > 4) formatted += `) ${digits.slice(4, 7)}`;
  if (digits.length > 7) formatted += `-${digits.slice(7, 9)}`;
  if (digits.length > 9) formatted += `-${digits.slice(9, 11)}`;
  
  return formatted;
};