import React, { useState, useCallback, useEffect } from 'react';
import { format } from 'date-fns';
import { studio } from '../data/studio';
import Calendar from './Calendar';
import TimeSlots from './TimeSlots';
import Modal from './Modal';
import { termsContent, privacyContent } from '../data/terms';
import { mockAvailability } from '../services/calendar/mock';
import { telegramNotificationService } from '../services/telegram/sendBooking';

// Валидация телефона с помощью регулярного выражения
const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^(\+7|7|8)?[\s-]?\(?[489][0-9]{2}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/;
  return phoneRegex.test(phone.replace(/\D/g, ''));
};

// Кастомный хук для маски телефона
const usePhoneMask = (initialValue: string = '') => {
  const [value, setValue] = useState(initialValue);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputVal = e.target.value.replace(/\D/g, '');
    let formattedVal = '';

    if (inputVal.length > 0) {
      formattedVal = '+7 ';
      if (inputVal.length > 1) {
        formattedVal += '(' + inputVal.slice(1, 4);
      }
      if (inputVal.length > 4) {
        formattedVal += ') ' + inputVal.slice(4, 7);
      }
      if (inputVal.length > 7) {
        formattedVal += '-' + inputVal.slice(7, 9);
      }
      if (inputVal.length > 9) {
        formattedVal += '-' + inputVal.slice(9, 11);
      }
    }

    setValue(formattedVal);
  };

  return { value, handleChange };
};

// Компонент для текстового поля
interface InputFieldProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  error?: string;
}

const InputField = React.memo(({ 
  label, 
  value, 
  onChange, 
  type = "text", 
  required = true, 
  error 
}: InputFieldProps) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <input
      type={type}
      value={value}
      onChange={onChange}
      className={`w-full p-3 border ${
        error ? 'border-red-500' : 'border-gray-300'
      } rounded-lg focus:ring-2 focus:ring-indigo-500`}
      required={required}
    />
    {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
  </div>
));

// Компонент для чекбокса с ссылкой
interface CheckboxFieldProps {
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
  linkText?: string;
  onLinkClick?: () => void;
}

const CheckboxField = React.memo(({ checked, onChange, label, linkText, onLinkClick }: CheckboxFieldProps) => (
  <label className="flex items-start space-x-3">
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="mt-1"
      required
    />
    <span className="text-sm text-gray-600">
      {label}{' '}
      {linkText && (
        <button
          type="button"
          onClick={onLinkClick}
          className="text-indigo-600 hover:underline"
        >
          {linkText}
        </button>
      )}
    </span>
  </label>
));

export default function BookingForm() {
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTimes, setSelectedTimes] = useState<string[]>([]);
  const [name, setName] = useState('');
  const { value: phone, handleChange: handlePhoneChange } = usePhoneMask();
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  
  // Состояния для ошибок
  const [nameError, setNameError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Прогрессивное улучшение: валидация в реальном времени
  useEffect(() => {
    if (name.length > 0 && name.length < 2) {
      setNameError('Имя слишком короткое');
    } else {
      setNameError('');
    }
  }, [name]);

  useEffect(() => {
    if (phone && !validatePhone(phone)) {
      setPhoneError('Некорректный номер телефона');
    } else {
      setPhoneError('');
    }
  }, [phone]);

  const handleTimeSelect = useCallback((time: string) => {
    setSelectedTimes(prev => {
      if (prev.includes(time)) {
        return prev.filter(t => t !== time);
      }
      return [...prev, time].sort();
    });
  }, []);

  const totalPrice = selectedTimes.length * studio.pricePerHour;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Валидация перед отправкой
    let hasError = false;
    
    if (!name || name.length < 2) {
      setNameError('Введите корректное имя');
      hasError = true;
    }
    
    if (!validatePhone(phone)) {
      setPhoneError('Введите корректный номер телефона');
      hasError = true;
    }
    
    if (hasError) return;

    setIsSubmitting(true);

    const bookingData = {
      date: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : '',
      times: selectedTimes,
      name,
      phone: phone.replace(/\D/g, ''), // Очистка номера от форматирования
      totalPrice,
      id: `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    
    try {
      // Создание события в календаре
      await mockAvailability.createBookingEvent({
        date: bookingData.date,
        startTime: selectedTimes[0],
        name: bookingData.name,
        phone: bookingData.phone,
        times: bookingData.times
      });

      // Параллельная отправка Telegram-уведомления
      try {
        await telegramNotificationService.sendBookingNotification(bookingData);
        console.log('Telegram notification sent successfully');
      } catch (telegramError) {
        console.error('Failed to send Telegram notification:', telegramError);
      }

      console.log('Booking submitted:', bookingData);
      alert('Заявка отправлена! Мы свяжемся с вами в ближайшее время.');
      
      // Сброс формы после успешной отправки
      setSelectedDate(null);
      setSelectedTimes([]);
      setName('');
      handlePhoneChange({ target: { value: '' } } as React.ChangeEvent<HTMLInputElement>);
      setTermsAccepted(false);
      setPrivacyAccepted(false);
    } catch (error) {
      console.error('Failed to create booking events:', error);
      alert('Не удалось создать бронирование. Пожалуйста, попробуйте еще раз.');
    } finally {
      setIsSubmitting(false);
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
            <InputField
              label="Ваше имя"
              value={name}
              onChange={(e) => setName(e.target.value)}
              error={nameError}
            />
            <InputField
              label="Телефон"
              value={phone}
              onChange={handlePhoneChange}
              type="tel"
              error={phoneError}
            />

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Детали бронирования</h4>
              <div className="space-y-2 text-sm text-gray-600">
                {selectedDate && (
                  <p>Дата: {format(selectedDate, 'dd.MM.yyyy')}</p>
                )}
                {selectedTimes.length > 0 && (
                  <p>Время: {selectedTimes.join(', ')}</p>
                )}
                <p className="text-lg font-bold text-indigo-600">
                  Итого: {totalPrice} ₽
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <CheckboxField
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                label="Я принимаю условия"
                linkText="публичной оферты"
                onLinkClick={() => setShowTermsModal(true)}
              />
              <CheckboxField
                checked={privacyAccepted}
                onChange={(e) => setPrivacyAccepted(e.target.checked)}
                label="Я согласен на"
                linkText="обработку персональных данных"
                onLinkClick={() => setShowPrivacyModal(true)}
              />
            </div>

            <button
              type="submit"
              disabled={
                !selectedDate || 
                selectedTimes.length === 0 || 
                !termsAccepted || 
                !privacyAccepted || 
                !!nameError || 
                !!phoneError ||
                isSubmitting
              }
              className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Отправка...' : 'Забронировать'}
            </button>
          </form>
        </div>

        {/* Модальные окна для терминов и политики конфиденциальности */}
        {showTermsModal && (
          <Modal 
            isOpen={true}
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
        )}
        {showPrivacyModal && (
          <Modal 
            isOpen={true}
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
        )}
      </div>
    </section>
  );
}