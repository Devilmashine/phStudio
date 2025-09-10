/**
 * Booking Details Form Component
 * Форма для деталей бронирования
 */

import React from 'react';
import { Controller, Control, FieldErrors } from 'react-hook-form';
import { BookingPriority } from '../../../stores/types';

interface BookingDetailsFormProps {
  control: Control<any>;
  errors: FieldErrors<any>;
  totalPrice: number;
  selectedSlots: string[];
}

const EQUIPMENT_OPTIONS = [
  { value: 'professional_lighting', label: 'Профессиональное освещение', price: 500 },
  { value: 'backdrop_white', label: 'Белый фон', price: 200 },
  { value: 'backdrop_black', label: 'Черный фон', price: 200 },
  { value: 'backdrop_colored', label: 'Цветной фон', price: 300 },
  { value: 'reflectors', label: 'Отражатели', price: 150 },
  { value: 'tripods', label: 'Штативы', price: 100 },
  { value: 'props', label: 'Реквизит', price: 400 },
  { value: 'smoke_machine', label: 'Дым-машина', price: 600 },
];

export const BookingDetailsForm: React.FC<BookingDetailsFormProps> = ({
  control,
  errors,
  totalPrice,
  selectedSlots
}) => {
  return (
    <div className="space-y-6">
      {/* Equipment Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Дополнительное оборудование
        </label>
        
        <Controller
          name="equipment_requested"
          control={control}
          render={({ field: { value = [], onChange } }) => (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {EQUIPMENT_OPTIONS.map((equipment) => (
                <label
                  key={equipment.value}
                  className="relative flex items-start p-3 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <div className="flex items-center h-5">
                    <input
                      type="checkbox"
                      checked={value.includes(equipment.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          onChange([...value, equipment.value]);
                        } else {
                          onChange(value.filter((item: string) => item !== equipment.value));
                        }
                      }}
                      className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
                    />
                  </div>
                  <div className="ml-3 text-sm flex-1">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {equipment.label}
                    </span>
                    <span className="block text-gray-500 dark:text-gray-400">
                      +{equipment.price} ₽/час
                    </span>
                  </div>
                </label>
              ))}
            </div>
          )}
        />
        
        {errors.equipment_requested && (
          <p className="mt-1 text-sm text-red-600">{errors.equipment_requested.message}</p>
        )}
      </div>

      {/* Special Requirements */}
      <Controller
        name="special_requirements"
        control={control}
        render={({ field }) => (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Особые требования
            </label>
            <textarea
              {...field}
              rows={3}
              placeholder="Укажите любые особые требования или пожелания..."
              className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            />
            {errors.special_requirements && (
              <p className="mt-1 text-sm text-red-600">{errors.special_requirements.message}</p>
            )}
          </div>
        )}
      />

      {/* Notes */}
      <Controller
        name="notes"
        control={control}
        render={({ field }) => (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Дополнительные заметки
            </label>
            <textarea
              {...field}
              rows={2}
              placeholder="Дополнительная информация..."
              className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            />
            {errors.notes && (
              <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
            )}
          </div>
        )}
      />

      {/* Priority */}
      <Controller
        name="priority"
        control={control}
        render={({ field }) => (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Приоритет бронирования
            </label>
            <select
              {...field}
              className="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            >
              <option value={BookingPriority.NORMAL}>Обычный</option>
              <option value={BookingPriority.HIGH}>Высокий</option>
              <option value={BookingPriority.URGENT}>Срочный</option>
            </select>
            {errors.priority && (
              <p className="mt-1 text-sm text-red-600">{errors.priority.message}</p>
            )}
          </div>
        )}
      />

      {/* Price Summary */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Стоимость бронирования
        </h4>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">
              Базовая стоимость ({selectedSlots.length} час{selectedSlots.length > 1 ? (selectedSlots.length > 4 ? 'ов' : 'а') : ''}):
            </span>
            <span className="text-gray-900 dark:text-white">
              {(2000 * selectedSlots.length).toLocaleString('ru-RU')} ₽
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Дополнительное оборудование:</span>
            <span className="text-gray-900 dark:text-white">
              {(totalPrice - (2000 * selectedSlots.length)).toLocaleString('ru-RU')} ₽
            </span>
          </div>
          
          <hr className="border-gray-300 dark:border-gray-600" />
          
          <div className="flex justify-between text-base font-semibold">
            <span className="text-gray-900 dark:text-white">Итого:</span>
            <span className="text-indigo-600 dark:text-indigo-400">
              {totalPrice.toLocaleString('ru-RU')} ₽
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingDetailsForm;
