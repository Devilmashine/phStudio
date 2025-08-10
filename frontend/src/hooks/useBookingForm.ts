import { useState, useMemo } from 'react';
import { format } from 'date-fns';
import { useBookingValidation } from './useBookingValidation';
import { createBooking } from '../services/booking'; 
import { studio } from '../data/studio';
import { useToast } from '../components/Toast';

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
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { formErrors, validateForm } = useBookingValidation({
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
    setSelectedTimes(prev => {
      if (prev.includes(time)) {
        return prev.filter(t => t !== time);
      }
      return [...prev, time].sort();
    });
  };

  const handleDateChange = (date: Date | null) => {
    setSelectedDate(date);
    setSelectedTimes([]);
  };

  const handleSubmit = async (e: React.FormEvent, totalPrice: number) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const bookingData = {
      date: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : '',
      times: selectedTimes,
      name: name.trim(),
      phone: phone.trim(),
      totalPrice
    };

    setIsSubmitting(true);
    try {
      await createBooking(bookingData);
      toast.show('Заявка успешно отправлена! Мы свяжемся с вами.');
      handleCloseSuccess(); // Сбрасываем форму
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Произошла неизвестная ошибка.';
      toast.show(`Ошибка: ${errorMessage}`);
      console.error('Booking submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCloseSuccess = () => {
    setShowSuccessModal(false);
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
    showSuccessModal,
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
    handleCloseSuccess,
    totalPrice
  };
}