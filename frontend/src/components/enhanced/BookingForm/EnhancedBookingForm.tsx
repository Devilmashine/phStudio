/**
 * Enhanced Booking Form
 * Интеграция с новым enhanced backend API и Zustand store
 */

import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  CreateBookingRequest,
  SpaceType,
  BookingPriority,
  BookingSource
} from '../../../stores/types';
import { useBookingStore, useUIStore } from '../../../stores';
import { EnhancedCalendar } from './EnhancedCalendar';
import { EnhancedTimeSlots } from './EnhancedTimeSlots';
import { ClientInfoForm } from './ClientInfoForm';
import { BookingDetailsForm } from './BookingDetailsForm';
import { TermsAndConditions } from './TermsAndConditions';
import LoadingSpinner from '../../common/LoadingSpinner';

// Validation schema using Zod
const bookingSchema = z.object({
  client_name: z.string()
    .min(2, 'Имя должно содержать минимум 2 символа')
    .max(100, 'Имя не может превышать 100 символов')
    .regex(/^[а-яА-ЯёЁa-zA-Z\s-]+$/, 'Имя может содержать только буквы, пробелы и дефисы'),
  
  client_phone: z.string()
    .min(10, 'Номер телефона должен содержать минимум 10 цифр')
    .regex(/^(\+7|7|8)?[\s-]?\(?[489][0-9]{2}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/, 
           'Введите корректный российский номер телефона'),
  
  client_email: z.string()
    .email('Введите корректный email адрес')
    .optional()
    .or(z.literal('')),
  
  booking_date: z.string()
    .min(1, 'Выберите дату бронирования'),
  
  start_time: z.string()
    .min(1, 'Выберите время начала'),
  
  end_time: z.string()
    .min(1, 'Выберите время окончания'),
  
  space_type: z.nativeEnum(SpaceType, {
    errorMap: () => ({ message: 'Выберите тип студии' })
  }),
  
  equipment_requested: z.array(z.string()).optional(),
  
  special_requirements: z.string()
    .max(1000, 'Особые требования не могут превышать 1000 символов')
    .optional(),
  
  notes: z.string()
    .max(500, 'Заметки не могут превышать 500 символов')
    .optional(),
  
  priority: z.nativeEnum(BookingPriority).optional(),
  
  // Terms acceptance
  terms_accepted: z.boolean()
    .refine(val => val === true, 'Необходимо принять условия публичной оферты'),
  
  privacy_accepted: z.boolean()
    .refine(val => val === true, 'Необходимо дать согласие на обработку персональных данных'),
  
  studio_rules_accepted: z.boolean()
    .refine(val => val === true, 'Необходимо ознакомиться с правилами студии'),
}).refine((data) => {
  // Validate that end_time is after start_time
  const startTime = new Date(`${data.booking_date}T${data.start_time}`);
  const endTime = new Date(`${data.booking_date}T${data.end_time}`);
  return endTime > startTime;
}, {
  message: 'Время окончания должно быть позже времени начала',
  path: ['end_time']
});

type BookingFormData = z.infer<typeof bookingSchema>;

interface EnhancedBookingFormProps {
  onSuccess?: (bookingId: number) => void;
  onCancel?: () => void;
  initialData?: Partial<CreateBookingRequest>;
  source?: BookingSource;
}

export const EnhancedBookingForm: React.FC<EnhancedBookingFormProps> = ({
  onSuccess,
  onCancel,
  initialData,
  source = BookingSource.WEBSITE
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTimeSlots, setSelectedTimeSlots] = useState<string[]>([]);
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [totalPrice, setTotalPrice] = useState(0);

  const { createBooking, isCreating, error } = useBookingStore();
  const { showSuccess, showError } = useUIStore();

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    trigger,
  } = useForm<BookingFormData>({
    resolver: zodResolver(bookingSchema),
    mode: 'onChange',
    defaultValues: {
      client_name: initialData?.client_name || '',
      client_phone: initialData?.client_phone || '',
      client_email: initialData?.client_email || '',
      space_type: initialData?.space_type || SpaceType.MAIN_STUDIO,
      equipment_requested: initialData?.equipment_requested || [],
      special_requirements: initialData?.special_requirements || '',
      notes: initialData?.notes || '',
      priority: initialData?.priority || BookingPriority.NORMAL,
      terms_accepted: false,
      privacy_accepted: false,
      studio_rules_accepted: false,
    },
  });

  const watchedValues = watch();

  // Calculate total price based on selected time slots and options
  useEffect(() => {
    const basePrice = 2000; // Base price per hour
    const equipmentPrice = (watchedValues.equipment_requested?.length || 0) * 300;
    const hours = selectedTimeSlots.length;
    const calculated = (basePrice * hours) + equipmentPrice;
    setTotalPrice(calculated);
  }, [selectedTimeSlots, watchedValues.equipment_requested]);

  // Update form values when date/time changes
  useEffect(() => {
    if (selectedDate) {
      setValue('booking_date', selectedDate.toISOString().split('T')[0]);
      trigger('booking_date');
    }
  }, [selectedDate, setValue, trigger]);

  useEffect(() => {
    if (selectedTimeSlots.length > 0) {
      setValue('start_time', selectedTimeSlots[0]);
      setValue('end_time', selectedTimeSlots[selectedTimeSlots.length - 1].replace(':', '') === '2300' 
        ? '23:59' 
        : `${parseInt(selectedTimeSlots[selectedTimeSlots.length - 1].split(':')[0]) + 1}:00`);
      trigger(['start_time', 'end_time']);
    }
  }, [selectedTimeSlots, setValue, trigger]);

  const onSubmit = async (data: BookingFormData) => {
    try {
      const bookingData: CreateBookingRequest = {
        client_name: data.client_name,
        client_phone: data.client_phone,
        client_email: data.client_email || undefined,
        booking_date: data.booking_date,
        start_time: `${data.booking_date}T${data.start_time}:00.000Z`,
        end_time: `${data.booking_date}T${data.end_time}:00.000Z`,
        space_type: data.space_type,
        equipment_requested: data.equipment_requested,
        special_requirements: data.special_requirements,
        notes: data.notes,
        source,
        priority: data.priority,
      };

      const booking = await createBooking(bookingData);
      
      showSuccess('Бронирование успешно создано!', 'Успех');
      onSuccess?.(booking.id);
    } catch (error: any) {
      showError(error.message || 'Ошибка при создании бронирования', 'Ошибка');
    }
  };

  const handleNextStep = async () => {
    let fieldsToValidate: (keyof BookingFormData)[] = [];

    switch (currentStep) {
      case 1:
        fieldsToValidate = ['booking_date', 'start_time', 'end_time', 'space_type'];
        break;
      case 2:
        fieldsToValidate = ['client_name', 'client_phone', 'client_email'];
        break;
      case 3:
        fieldsToValidate = ['equipment_requested', 'special_requirements', 'notes', 'priority'];
        break;
      case 4:
        fieldsToValidate = ['terms_accepted', 'privacy_accepted', 'studio_rules_accepted'];
        break;
    }

    const isStepValid = await trigger(fieldsToValidate);
    
    if (isStepValid) {
      setCurrentStep(prev => Math.min(prev + 1, 5));
    }
  };

  const handlePrevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Выберите дату и время
            </h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <EnhancedCalendar
                  selectedDate={selectedDate}
                  onDateSelect={setSelectedDate}
                  minDate={new Date()}
                  maxDate={new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)} // 90 days from now
                />
              </div>
              
              <div>
                {selectedDate && (
                  <EnhancedTimeSlots
                    date={selectedDate}
                    selectedSlots={selectedTimeSlots}
                    onSlotsChange={setSelectedTimeSlots}
                    availableSlots={availableSlots}
                    spaceType={watchedValues.space_type}
                  />
                )}
              </div>
            </div>

            <Controller
              name="space_type"
              control={control}
              render={({ field }) => (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Тип студии
                  </label>
                  <select
                    {...field}
                    className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value={SpaceType.MAIN_STUDIO}>Основная студия</option>
                    <option value={SpaceType.SMALL_STUDIO}>Малая студия</option>
                    <option value={SpaceType.OUTDOOR_AREA}>Открытая площадка</option>
                  </select>
                  {errors.space_type && (
                    <p className="mt-1 text-sm text-red-600">{errors.space_type.message}</p>
                  )}
                </div>
              )}
            />
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Контактная информация
            </h3>
            
            <ClientInfoForm
              control={control}
              errors={errors}
            />
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Детали бронирования
            </h3>
            
            <BookingDetailsForm
              control={control}
              errors={errors}
              totalPrice={totalPrice}
              selectedSlots={selectedTimeSlots}
            />
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Условия и соглашения
            </h3>
            
            <TermsAndConditions
              control={control}
              errors={errors}
            />
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Подтверждение бронирования
            </h3>
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Клиент:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">{watchedValues.client_name}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Телефон:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">{watchedValues.client_phone}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Дата:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">
                    {selectedDate?.toLocaleDateString('ru-RU')}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Время:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">
                    {selectedTimeSlots.join(', ')}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Студия:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">
                    {watchedValues.space_type === SpaceType.MAIN_STUDIO && 'Основная студия'}
                    {watchedValues.space_type === SpaceType.SMALL_STUDIO && 'Малая студия'}
                    {watchedValues.space_type === SpaceType.OUTDOOR_AREA && 'Открытая площадка'}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Итого:</span>
                  <span className="ml-2 text-xl font-bold text-indigo-600 dark:text-indigo-400">
                    {totalPrice.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
              Ошибка загрузки формы
            </h3>
            <div className="mt-2 text-sm text-red-700 dark:text-red-300">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4, 5].map((step) => (
            <div
              key={step}
              className={`flex items-center ${
                step < 5 ? 'flex-1' : ''
              }`}
            >
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                  currentStep >= step
                    ? 'bg-indigo-600 border-indigo-600 text-white'
                    : 'border-gray-300 text-gray-500'
                }`}
              >
                {step}
              </div>
              {step < 5 && (
                <div
                  className={`flex-1 h-0.5 ml-4 ${
                    currentStep > step ? 'bg-indigo-600' : 'bg-gray-300'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 text-center">
          Шаг {currentStep} из 5
        </div>
      </div>

      {/* Form content */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          {renderStepContent()}
        </div>

        {/* Navigation buttons */}
        <div className="flex justify-between">
          <div>
            {currentStep > 1 && (
              <button
                type="button"
                onClick={handlePrevStep}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Назад
              </button>
            )}
          </div>

          <div className="flex space-x-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Отмена
              </button>
            )}

            {currentStep < 5 ? (
              <button
                type="button"
                onClick={handleNextStep}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Далее
              </button>
            ) : (
              <button
                type="submit"
                disabled={!isValid || isCreating}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isCreating ? (
                  <>
                    <LoadingSpinner className="w-4 h-4 mr-2" />
                    Создание...
                  </>
                ) : (
                  'Создать бронирование'
                )}
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};

export default EnhancedBookingForm;
