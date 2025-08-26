import { useState, useMemo } from 'react';
import { format } from 'date-fns';
import { useBookingValidation } from './useBookingValidation';
import { createBooking } from '../services/booking'; 
import { studio } from '../data/studio';
import { useToast } from '../components/Toast';
import consentService from '../services/consentService';

export function useBookingForm() {
  const toast = useToast();
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTimes, setSelectedTimes] = useState<string[]>([]);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('+7');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { formErrors, validateForm, clearErrors } = useBookingValidation({
    selectedDate,
    selectedTimes,
    name,
    phone,
    termsAccepted,
    privacyAccepted
  });

  const totalPrice = useMemo(() => {
    return selectedTimes.length * studio.pricePerHour;
  }, [selectedTimes]);

  const handleTimeSelect = (time: string) => {
    clearErrors(); // Очищаем ошибки при выборе времени
    setSelectedTimes(prev => {
      if (prev.includes(time)) {
        return prev.filter(t => t !== time);
      }
      return [...prev, time].sort();
    });
  };

  const handleDateChange = (date: Date | null) => {
    clearErrors(); // Очищаем ошибки при выборе даты
    setSelectedDate(date);
    setSelectedTimes([]);
  };

  const handleSubmit = async (e: React.FormEvent, totalPrice: number) => {
    e.preventDefault();
    console.log('Form submitted with data:', {
      selectedDate,
      selectedTimes,
      name,
      phone,
      termsAccepted,
      privacyAccepted,
      totalPrice
    });
    
    // Clear any existing errors before validation
    clearErrors();
    
    if (!validateForm()) {
      console.log('Form validation failed:', formErrors);
      toast.show('Пожалуйста, исправьте ошибки в форме.');
      return;
    }

    if (!selectedDate) {
      console.error('selectedDate is null, cannot proceed');
      toast.show('Пожалуйста, выберите дату.');
      return;
    }

    const bookingData = {
      date: format(selectedDate, 'yyyy-MM-dd'),
      times: selectedTimes,
      name: name.trim(),
      phone: phone.trim(),
      totalPrice
    };

    console.log('Submitting booking data:', bookingData);
    setIsSubmitting(true);
    
    try {
      // First record the consent (required by 152-ФЗ)
      console.log('Recording booking consent...');
      await consentService.recordBookingConsent({
        ...bookingData,
        client_phone: phone.trim(),
        client_name: name.trim()
      });
      
      // Then create the booking
      const result = await createBooking(bookingData);
      console.log('Booking submitted successfully:', result);
      toast.show('Заявка успешно отправлена! Мы свяжемся с вами.');
      resetForm(); // Сбрасываем форму
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Произошла неизвестная ошибка.';
      console.error('Booking submission error:', error);
      toast.show(`Ошибка: ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedDate(null);
    setSelectedTimes([]);
    setName('');
    setPhone('+7');
    setTermsAccepted(false);
    setPrivacyAccepted(false);
  };

  return {
    selectedDate,
    selectedTimes,
    name,
    phone,
    termsAccepted,
    privacyAccepted,
    showTermsModal,
    showPrivacyModal,
    isSubmitting,
    formErrors,
    setName,
    setPhone,
    setTermsAccepted,
    setPrivacyAccepted,
    setShowTermsModal,
    setShowPrivacyModal,
    handleTimeSelect,
    handleDateChange,
    handleSubmit,
    resetForm,
    totalPrice
  };
}