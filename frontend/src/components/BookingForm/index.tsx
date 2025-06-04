import React, { useState } from 'react';
import { format } from 'date-fns';
import { studio } from '../../data/studio';
import Calendar from '../Calendar';
import TimeSlots from '../TimeSlots';
import Modal from '../Modal';
import { termsContent, privacyContent } from '../../data/terms';
import BookingDetails from './BookingDetails';
import TermsCheckboxes from './TermsCheckboxes';
import ContactForm from './ContactForm';
import { validatePhone } from '../../utils/validation/phoneValidation';
import { createYandexCalendarLink } from '../../utils/calendar';

const BookingForm = React.memo(() => {
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTimes, setSelectedTimes] = useState<string[]>([]);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [formErrors, setFormErrors] = useState<string[]>([]);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [calendarUrl, setCalendarUrl] = useState<string>('');

  const handleTimeSelect = (time: string) => {
    setSelectedTimes(prev => {
      if (prev.includes(time)) {
        return prev.filter(t => t !== time);
      }
      return [...prev, time].sort();
    });
  };

  const totalPrice = selectedTimes.length * studio.pricePerHour;

  const validateForm = (): boolean => {
    const errors: string[] = [];

    if (!selectedDate) {
      errors.push('Выберите дату');
    }

    if (selectedTimes.length === 0) {
      errors.push('Выберите время');
    }

    if (!name.trim()) {
      errors.push('Введите имя');
    } else if (name.trim().length < 2) {
      errors.push('Имя должно содержать минимум 2 символа');
    }

    if (!phone.trim()) {
      errors.push('Введите номер телефона');
    } else if (!validatePhone(phone)) {
      errors.push('Введите корректный номер телефона');
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

  const handleSubmit = (e: React.FormEvent) => {
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

    // Generate calendar URL
    const url = createYandexCalendarLink(bookingData);
    setCalendarUrl(url);
    
    console.log('Booking submitted:', bookingData);
    setShowSuccessModal(true);
  };

  const handleCloseSuccess = () => {
    setShowSuccessModal(false);
    // Reset form
    setSelectedDate(null);
    setSelectedTimes([]);
    setName('');
    setPhone('');
    setTermsAccepted(false);
    setPrivacyAccepted(false);
    setFormErrors([]);
    // Clean up the URL object
    if (calendarUrl) {
      URL.revokeObjectURL(calendarUrl);
      setCalendarUrl('');
    }
  };

  return (
    <section id="booking" className="py-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Забронировать студию</h2>
          <p className="text-xl text-gray-600">Выберите удобное время для съёмки</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="space-y-6">
            <Calendar
              selectedDate={selectedDate}
              onChange={(date) => {
                setSelectedDate(date);
                setSelectedTimes([]);
              }}
            />

            {selectedDate && (
              <TimeSlots
                date={selectedDate}
                selectedTimes={selectedTimes}
                onSelectTime={handleTimeSelect}
              />
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-xl shadow-lg">
            {formErrors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm font-medium text-red-800 mb-2">Пожалуйста, исправьте следующие ошибки:</p>
                <ul className="list-disc list-inside text-sm text-red-700">
                  {formErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            <ContactForm
              name={name}
              phone={phone}
              onNameChange={setName}
              onPhoneChange={setPhone}
            />

            <BookingDetails
              selectedDate={selectedDate}
              selectedTimes={selectedTimes}
              totalPrice={totalPrice}
            />

            <TermsCheckboxes
              termsAccepted={termsAccepted}
              privacyAccepted={privacyAccepted}
              onTermsChange={setTermsAccepted}
              onPrivacyChange={setPrivacyAccepted}
              onShowTerms={() => setShowTermsModal(true)}
              onShowPrivacy={() => setShowPrivacyModal(true)}
            />

            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Отправить заявку
            </button>
          </form>
        </div>
      </div>

      <Modal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        title="Публичная оферта"
      >
        <div className="prose prose-sm max-w-none">
          {termsContent.split('\n\n').map((paragraph, index) => (
            <p key={index} className="mb-4">
              {paragraph}
            </p>
          ))}
        </div>
      </Modal>

      <Modal
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        title="Политика обработки персональных данных"
      >
        <div className="prose prose-sm max-w-none">
          {privacyContent.split('\n\n').map((paragraph, index) => (
            <p key={index} className="mb-4">
              {paragraph}
            </p>
          ))}
        </div>
      </Modal>

      <Modal
        isOpen={showSuccessModal}
        onClose={handleCloseSuccess}
        title="Заявка отправлена!"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Спасибо за вашу заявку! Мы свяжемся с вами в ближайшее время для подтверждения бронирования.
          </p>
          <div className="flex justify-center">
            <a
              href={calendarUrl}
              download="booking.ics"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              Добавить в календарь
            </a>
          </div>
        </div>
      </Modal>
    </section>
  );
});

export default BookingForm;