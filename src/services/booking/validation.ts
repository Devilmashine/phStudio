import { BookingData } from '../../types';
import { validatePhone } from '../../utils/validation/phoneValidation';
import { validateName } from '../../utils/validation/nameValidation';

/**
 * Валидирует данные бронирования.
 */
export function validateBooking(booking: BookingData): string[] {
  const errors: string[] = [];

  // Проверка даты
  if (!booking.date) {
    errors.push('Выберите дату');
  }

  // Проверка времени
  if (booking.times.length === 0) {
    errors.push('Выберите время');
  }

  // Проверка имени
  const nameError = validateName(booking.name);
  if (nameError) {
    errors.push(nameError);
  }

  // Проверка телефона
  if (!validatePhone(booking.phone)) {
    errors.push('Введите корректный номер телефона');
  }

  return errors;
}