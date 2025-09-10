/**
 * Input Atom Component
 * Базовый компонент поля ввода следуя Atomic Design
 */

import React, { forwardRef } from 'react';
import { ExclamationCircleIcon } from '@heroicons/react/24/outline';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'default' | 'filled' | 'outlined';
  inputSize?: 'sm' | 'md' | 'lg';
}

const variantClasses = {
  default: 'border-gray-300 dark:border-gray-600 focus:border-indigo-500 focus:ring-indigo-500',
  filled: 'border-transparent bg-gray-100 dark:bg-gray-700 focus:border-indigo-500 focus:ring-indigo-500 focus:bg-white dark:focus:bg-gray-800',
  outlined: 'border-2 border-gray-300 dark:border-gray-600 focus:border-indigo-500 focus:ring-0',
};

const sizeClasses = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-3 py-2 text-sm',
  lg: 'px-4 py-3 text-base',
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({
    label,
    error,
    helperText,
    leftIcon,
    rightIcon,
    variant = 'default',
    inputSize = 'md',
    className = '',
    id,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const hasError = Boolean(error);

    const baseClasses = `
      block w-full rounded-md shadow-sm 
      dark:bg-gray-800 dark:text-white 
      placeholder-gray-400 dark:placeholder-gray-500
      focus:outline-none focus:ring-1
      disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
      dark:disabled:bg-gray-700 dark:disabled:text-gray-400
    `;

    const inputClasses = `
      ${baseClasses}
      ${hasError 
        ? 'border-red-300 dark:border-red-600 focus:border-red-500 focus:ring-red-500' 
        : variantClasses[variant]
      }
      ${sizeClasses[inputSize]}
      ${leftIcon ? 'pl-10' : ''}
      ${rightIcon || hasError ? 'pr-10' : ''}
      ${className}
    `.trim().replace(/\s+/g, ' ');

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            {label}
            {props.required && (
              <span className="text-red-500 ml-1">*</span>
            )}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="h-5 w-5 text-gray-400">
                {leftIcon}
              </div>
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={inputClasses}
            {...props}
          />

          {(rightIcon || hasError) && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              {hasError ? (
                <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
              ) : (
                <div className="h-5 w-5 text-gray-400">
                  {rightIcon}
                </div>
              )}
            </div>
          )}
        </div>

        {(error || helperText) && (
          <div className="mt-2">
            {error && (
              <p className="text-sm text-red-600 dark:text-red-400">
                {error}
              </p>
            )}
            {helperText && !error && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {helperText}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
