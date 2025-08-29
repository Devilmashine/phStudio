import React from 'react';

interface InputFieldProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  error?: string;
  id?: string;
}

const InputField = React.memo(({
  label,
  value,
  onChange,
  type = "text",
  required = true,
  error,
  id
}: InputFieldProps) => (
  <div className="w-full">
    <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor={id || label}>{label}</label>
    <input
      id={id || label}
      type={type}
      value={value}
      onChange={onChange}
      className={`w-full p-3 border ${
        error ? 'border-red-500' : 'border-gray-300'
      } rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors duration-150`}
      required={required}
      aria-invalid={!!error}
      aria-describedby={error ? `${id || label}-error` : undefined}
    />
    {error && <p id={`${id || label}-error`} className="text-red-500 text-xs mt-1" role="alert">{error}</p>}
  </div>
));

export default InputField;
