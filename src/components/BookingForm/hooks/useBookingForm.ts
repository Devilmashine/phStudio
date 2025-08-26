import { useState, useCallback } from 'react';
import { BookingFormData } from '../types';
import { useFormValidation } from '../validation/useFormValidation';
import { formatPhoneNumber } from '../../../utils/validation/phoneValidation';

export const useBookingForm = () => {
  const [formData, setFormData] = useState<BookingFormData>({
    selectedDate: null,
    selectedTimes: [],
    name: '',
    phone: '+7',
    termsAccepted: false,
    privacyAccepted: false,
  });

  const { validateForm } = useFormValidation(formData);

  /**
   * Обновляет данные формы.
   * @param field - Поле формы, которое нужно обновить.
   * @param value - Новое значение поля.
   */
  const updateFormData = useCallback((field: keyof BookingFormData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: field === 'phone' ? formatPhoneNumber(value) : value,
    }));
  }, []);

  /**
   * Обрабатывает выбор времени.
   * @param time - Выбранное время.
   */
  const handleTimeSelect = useCallback((time: string) => {
    setFormData((prev) => ({
      ...prev,
      selectedTimes: prev.selectedTimes.includes(time)
        ? prev.selectedTimes.filter((t) => t !== time)
        : [...prev.selectedTimes, time].sort(),
    }));
  }, []);

  /**
   * Сбрасывает форму к начальным значениям.
   */
  const resetForm = useCallback(() => {
    setFormData({
      selectedDate: null,
      selectedTimes: [],
      name: '',
      phone: '+7',
      termsAccepted: false,
      privacyAccepted: false,
    });
  }, []);

  return {
    formData,
    updateFormData,
    handleTimeSelect,
    resetForm,
    validateForm,
  };
};