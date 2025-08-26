import { validatePhone, validateName } from '../utils/validation';
import { useState } from 'react';

interface ValidationProps {
  selectedDate: Date | null;
  selectedTimes: string[];
  name: string;
  phone: string;
  termsAccepted: boolean;
  privacyAccepted: boolean;
}

export function useBookingValidation({
  selectedDate,
  selectedTimes,
  name,
  phone,
  termsAccepted,
  privacyAccepted,
}: ValidationProps) {
  const [formErrors, setFormErrors] = useState<string[]>([]);

  const validateForm = (): boolean => {
    const errors: string[] = [];

    if (!selectedDate) {
      errors.push('Выберите дату бронирования');
    }

    if (selectedTimes.length === 0) {
      errors.push('Выберите хотя бы один временной слот');
    }

    if (!name.trim()) {
      errors.push('Пожалуйста, введите ваше имя');
    } else if (!validateName(name)) {
      errors.push('Имя должно содержать только русские буквы, пробелы или дефисы (от 2 до 50 символов)');
    }

    if (!phone.trim()) {
      errors.push('Пожалуйста, введите номер телефона');
    } else if (!validatePhone(phone)) {
      errors.push('Введите корректный российский мобильный номер (например, +7 (912) 345-67-89)');
    }

    if (!termsAccepted) {
      errors.push('Необходимо принять условия публичной оферты');
    }

    if (!privacyAccepted) {
      errors.push('Необходимо согласиться на обработку персональных данных');
    }

    setFormErrors(errors);
    return errors.length === 0;
  };

  // Функция для очистки ошибок
  const clearErrors = () => {
    setFormErrors([]);
  };

  return {
    validateForm,
    formErrors,
    clearErrors
  };
}