/**
 * Phone Input Component
 * Компонент для ввода номера телефона с маской
 */

import React, { forwardRef } from 'react';
import { IMaskInput } from 'react-imask';

interface PhoneInputProps {
  label?: string;
  placeholder?: string;
  required?: boolean;
  error?: string;
  className?: string;
  value?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  name?: string;
}

export const PhoneInput = forwardRef<HTMLInputElement, PhoneInputProps>(
  ({ label, placeholder, required, error, className = '', value = '', onChange, onBlur, name }, ref) => {
    return (
      <div className={className}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        
        <IMaskInput
          mask="+7 (000) 000-00-00"
          value={value}
          onAccept={(value: string) => onChange?.(value)}
          onBlur={onBlur}
          name={name}
          placeholder={placeholder}
          className={`block w-full rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
            error 
              ? 'border-red-300 dark:border-red-600' 
              : 'border-gray-300 dark:border-gray-600'
          }`}
          inputRef={ref}
        />
        
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);

PhoneInput.displayName = 'PhoneInput';

export default PhoneInput;
