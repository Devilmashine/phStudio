import { validatePhone } from '../../../utils/validation/phoneValidation';
import { validateName } from '../../../utils/validation/nameValidation';
import { BookingFormData } from '../types';

// Константы для сообщений об ошибках
const ERROR_MESSAGES = {
  DATE_REQUIRED: 'Выберите дату',
  TIME_REQUIRED: 'Выберите время',
  PHONE_INVALID: 'Введите корректный номер телефона в формате +7 (9XX) XXX-XX-XX',
  TERMS_NOT_ACCEPTED: 'Необходимо принять условия публичной оферты',
  PRIVACY_NOT_ACCEPTED: 'Необходимо согласиться на обработку персональных данных',
};

export const useFormValidation = (formData: BookingFormData) => {
  const validateForm = (): string[] => {
    const errors: string[] = [];

    // Проверка даты
    if (!formData.selectedDate) {
      errors.push(ERROR_MESSAGES.DATE_REQUIRED);
    }

    // Проверка времени
    if (formData.selectedTimes.length === 0) {
      errors.push(ERROR_MESSAGES.TIME_REQUIRED);
    }

    // Проверка имени
    const nameError = validateName(formData.name);
    if (nameError) {
      errors.push(nameError);
    }

    // Проверка телефона
    if (!validatePhone(formData.phone)) {
      errors.push(ERROR_MESSAGES.PHONE_INVALID);
    }

    // Проверка принятия условий
    if (!formData.termsAccepted) {
      errors.push(ERROR_MESSAGES.TERMS_NOT_ACCEPTED);
    }

    // Проверка согласия на обработку персональных данных
    if (!formData.privacyAccepted) {
      errors.push(ERROR_MESSAGES.PRIVACY_NOT_ACCEPTED);
    }

    return errors;
  };

  return { validateForm };
};