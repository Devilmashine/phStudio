import React from 'react';
import { formatPhoneNumber } from '../../utils/validation/phoneValidation';

interface PhoneInputProps {
  value: string;
  onChange: (value: string) => void;
  onBlur: () => void;
  error?: string;
}

const PhoneInput = React.memo(({ value, onChange, onBlur, error }: PhoneInputProps) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formattedPhone = formatPhoneNumber(e.target.value);
    onChange(formattedPhone);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Телефон
      </label>
      <input
        type="tel"
        value={value}
        onChange={handleChange}
        onBlur={onBlur}
        className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
        placeholder="+7 (9XX) XXX-XX-XX"
        required
      />
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
});

export default PhoneInput;