import React from 'react';

interface CheckboxFieldProps {
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
  linkText?: string;
  onLinkClick?: () => void;
  id?: string;
}

const CheckboxField = React.memo(({ checked, onChange, label, linkText, onLinkClick, id }: CheckboxFieldProps) => (
  <label htmlFor={id} className="flex items-start space-x-3 cursor-pointer select-none">
    <input
      id={id}
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="mt-1 accent-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors"
      required
      aria-checked={checked}
    />
    <span className="text-sm text-gray-600">
      {label}{' '}
      {linkText && (
        <button
          type="button"
          onClick={onLinkClick}
          className="text-indigo-600 hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
          tabIndex={0}
        >
          {linkText}
        </button>
      )}
    </span>
  </label>
));

export default CheckboxField;
