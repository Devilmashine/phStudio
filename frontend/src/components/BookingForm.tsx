import React, { useState, useCallback, useEffect } from 'react';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import { studio } from '../data/studio';
import Calendar from './Calendar';
import TimeSlots from './TimeSlots';
import Legend, { TimeSlotsLegendItems } from './common/Legend';
import Modal from './Modal';
import CheckboxField from './ui/CheckboxField';
import { termsContent } from '../data/terms';
import { createBooking } from '../services/booking';

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
  <div className="w-full">
    <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor={label}>{label}</label>
    <input
      id={label}
      type={type}
      value={value}
      onChange={onChange}
      className={`w-full p-3 border ${
        error ? 'border-red-500' : 'border-gray-300'
      } rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors duration-150`}
      required={required}
      aria-invalid={!!error}
      aria-describedby={error ? `${label}-error` : undefined}
    />
    {error && <p id={`${label}-error`} className="text-red-500 text-xs mt-1" role="alert">{error}</p>}
  </div>
));

export default function BookingForm() {
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTimes, setSelectedTimes] = useState<string[]>([]);
  const [name, setName] = useState('');
  const { value: phone, handleChange: handlePhoneChange } = usePhoneMask();
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [peopleCount, setPeopleCount] = useState(1);
  const [peopleError, setPeopleError] = useState('');
  const [studioRulesAccepted, setStudioRulesAccepted] = useState(false);
  const [showStudioRulesModal, setShowStudioRulesModal] = useState(false);
  
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

  useEffect(() => {
    if (peopleCount < 1) {
      setPeopleError('Укажите количество человек (минимум 1)');
    } else if (peopleCount > 30) {
      setPeopleError('Слишком много человек для одной брони');
    } else {
      setPeopleError('');
    }
  }, [peopleCount]);

  const handleTimeSelect = useCallback((time: string) => {
    setSelectedTimes(prev => {
      if (prev.includes(time)) {
        return prev.filter(t => t !== time);
      }
      return [...prev, time].sort();
    });
  }, []);

  // Пересчёт стоимости с учётом количества человек
  const basePeople = 5;
  const extraPeople = Math.max(0, peopleCount - basePeople);
  const extraFee = extraPeople * 200 * selectedTimes.length;
  const totalPrice = selectedTimes.length * studio.pricePerHour + extraFee;

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
    
    if (peopleCount < 1) {
      setPeopleError('Укажите количество человек (минимум 1)');
      hasError = true;
    } else if (peopleCount > 30) {
      setPeopleError('Слишком много человек для одной брони');
      hasError = true;
    } else {
      setPeopleError('');
    }
    
    if (hasError) return;

    setIsSubmitting(true);

    const bookingData = {
      date: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : '',
      times: selectedTimes,
      name,
      phone: phone.replace(/\D/g, ''),
      total_price: totalPrice, // snake_case для backend
      people_count: peopleCount, // snake_case для backend
      service: 'Студийная фотосессия',
      id: `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    
    try {
      // Use the real booking service instead of mock
      const bookingResponse = await createBooking({
        date: bookingData.date,
        times: bookingData.times,
        name: bookingData.name,
        phone: bookingData.phone,
        totalPrice: bookingData.total_price
      });

      console.log('Booking created successfully:', bookingResponse);
      
      // Verify booking was saved by checking availability for the booked slot
      try {
        const dateStr = format(selectedDate!, 'yyyy-MM-dd');
        const response = await fetch(`/api/calendar/day-details?date=${dateStr}`);
        if (response.ok) {
          const dayDetails = await response.json();
          const bookedSlot = dayDetails.slots.find((slot: any) => 
            selectedTimes.includes(slot.time) && !slot.available
          );
          
          if (bookedSlot) {
            console.log('✅ Booking verification successful - slot is now unavailable');
          } else {
            console.warn('⚠️ Booking verification failed - slot still appears available');
          }
        }
      } catch (verificationError) {
        console.warn('Could not verify booking:', verificationError);
      }
      
      // Show detailed success message with booking ID
      const successMessage = `Бронирование успешно создано!\n\n` +
        `🆔 Номер брони: ${bookingResponse.id}\n` +
        `📅 Дата: ${format(selectedDate!, 'dd.MM.yyyy')}\n` +
        `🕜 Время: ${selectedTimes.join(', ')}\n` +
        `💰 Сумма: ${totalPrice} ₽\n\n` +
        `Мы свяжемся с вами в ближайшее время!`;
      
      // Store booking ID for potential future reference
      sessionStorage.setItem('lastBookingId', bookingResponse.id.toString());
      
      alert(successMessage);
      
      // Reset form after successful booking
      setSelectedDate(null);
      setSelectedTimes([]);
      setName('');
      handlePhoneChange({ target: { value: '' } } as React.ChangeEvent<HTMLInputElement>);
      setTermsAccepted(false);
      setPrivacyAccepted(false);
      setPeopleCount(1);
      setStudioRulesAccepted(false);
      
      // Force calendar refresh by dispatching a custom event
      // This will tell calendar components to refresh their data
      window.dispatchEvent(new CustomEvent('bookingCreated', {
        detail: {
          bookingId: bookingResponse.id,
          date: bookingData.date,
          times: bookingData.times
        }
      }));
    } catch (error) {
      console.error('Failed to create booking:', error);
      const errorMessage = error instanceof Error ? error.message : 'Не удалось создать бронирование. Пожалуйста, попробуйте еще раз.';
      alert(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section id="booking" className="py-10 sm:py-16 md:py-20">
      <div className="max-w-6xl mx-auto px-2 sm:px-4 md:px-6 lg:px-8">
        <div className="text-center mb-10 md:mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2 md:mb-4">Забронировать студию</h2>
          <p className="text-base sm:text-xl text-gray-600">Выберите удобное время для съёмки</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12 items-start">
          <div className="space-y-6 sticky top-4 z-10">
            <Calendar
              selectedDate={selectedDate}
              onChange={(date) => {
                setSelectedDate(date);
                setSelectedTimes([]);
              }}
            />
            {selectedDate && (
              <div className="overflow-x-auto">
                <TimeSlots
                  date={selectedDate}
                  selectedTimes={selectedTimes}
                  onSelectTime={handleTimeSelect}
                />
                {/* Легенда для временных слотов */}
                <Legend 
                  items={TimeSlotsLegendItems} 
                  className="mt-3" 
                  compact={true}
                  size="sm"
                />
              </div>
            )}
          </div>
          <form onSubmit={handleSubmit} className="space-y-6 bg-white p-4 sm:p-6 md:p-8 rounded-xl shadow-lg w-full max-w-lg mx-auto lg:mx-0 overflow-auto" role="form" aria-label="Форма бронирования">
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
            <InputField
              label="Количество человек"
              value={peopleCount.toString()}
              onChange={e => setPeopleCount(Math.max(1, parseInt(e.target.value) || 1))}
              type="number"
              required
              error={peopleError}
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
              <label className="flex items-start space-x-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={privacyAccepted}
                  onChange={(e) => setPrivacyAccepted(e.target.checked)}
                  className="mt-1 accent-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors"
                  required
                />
                <span className="text-sm text-gray-600">
                  Я даю согласие на обработку персональных данных и принимаю условия{' '}
                  <Link to="/privacy" target="_blank" className="text-indigo-600 hover:underline">
                    Политики конфиденциальности
                  </Link>
                </span>
              </label>
              <CheckboxField
                checked={studioRulesAccepted}
                onChange={e => setStudioRulesAccepted(e.target.checked)}
                label="Я согласен с правилами студии"
                linkText="правилами студии"
                onLinkClick={() => setShowStudioRulesModal(true)}
              />
            </div>
            <button
              type="submit"
              disabled={
                !selectedDate || 
                selectedTimes.length === 0 || 
                !termsAccepted || 
                !privacyAccepted || 
                !studioRulesAccepted ||
                !!nameError || 
                !!phoneError ||
                !!peopleError ||
                isSubmitting
              }
              className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-busy={isSubmitting}
              aria-label="Забронировать студию"
            >
              {isSubmitting && (
                <svg className="animate-spin h-5 w-5 text-white mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                </svg>
              )}
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
        {showStudioRulesModal && (
          <Modal 
            isOpen={true}
            onClose={() => setShowStudioRulesModal(false)}
            title="Правила студии"
          >
            <div className="prose prose-sm max-w-none">
              <ul className="list-disc pl-5 space-y-2">
                <li>Максимум 5 человек бесплатно, за каждого дополнительного — 200 руб/час.</li>
                <li>В студии запрещено курить, распивать алкоголь, использовать открытый огонь.</li>
                <li>Использование реквизита и оборудования — бережно, после использования вернуть на место.</li>
                <li>Дети допускаются только в сопровождении взрослых.</li>
                <li>Время бронирования включает время на сборы и уборку.</li>
                <li>Запрещено шуметь, мешать другим арендаторам и нарушать общественный порядок.</li>
                <li>За порчу имущества взыскивается компенсация по оценке студии.</li>
                <li>Соблюдайте чистоту, уважайте персонал и других гостей.</li>
                <li>Администрация оставляет за собой право отказать в обслуживании без объяснения причин.</li>
                <li>Подробные правила — на сайте и у администратора.</li>
              </ul>
            </div>
          </Modal>
        )}
      </div>
    </section>
  );
}