/**
 * Button Atom Component
 * Базовый компонент кнопки следуя Atomic Design
 */

import React, { forwardRef } from 'react';
import { LoadingSpinner } from '../../common/LoadingSpinner';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'ghost';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

const variantClasses = {
  primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500 border-transparent',
  secondary: 'bg-white text-gray-700 hover:bg-gray-50 focus:ring-indigo-500 border-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 border-transparent',
  success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 border-transparent',
  warning: 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500 border-transparent',
  ghost: 'bg-transparent text-gray-600 hover:bg-gray-100 focus:ring-gray-500 border-transparent dark:text-gray-400 dark:hover:bg-gray-800',
};

const sizeClasses = {
  xs: 'px-2.5 py-1.5 text-xs',
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-4 py-2 text-base',
  xl: 'px-6 py-3 text-base',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    iconPosition = 'left',
    fullWidth = false,
    children,
    className = '',
    disabled,
    ...props
  }, ref) => {
    const baseClasses = `
      inline-flex items-center justify-center border font-medium rounded-md 
      shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 
      transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed
    `;

    const classes = `
      ${baseClasses}
      ${variantClasses[variant]}
      ${sizeClasses[size]}
      ${fullWidth ? 'w-full' : ''}
      ${className}
    `.trim().replace(/\s+/g, ' ');

    const isDisabled = disabled || loading;

    const renderIcon = (position: 'left' | 'right') => {
      if (loading && position === 'left') {
        return <LoadingSpinner className="w-4 h-4 mr-2" />;
      }
      
      if (icon && iconPosition === position) {
        return (
          <span className={`
            ${children ? (position === 'left' ? 'mr-2' : 'ml-2') : ''}
            ${size === 'xs' ? 'w-3 h-3' : 'w-4 h-4'}
          `}>
            {icon}
          </span>
        );
      }
      
      return null;
    };

    return (
      <button
        ref={ref}
        className={classes}
        disabled={isDisabled}
        {...props}
      >
        {renderIcon('left')}
        {loading && iconPosition === 'right' && children && (
          <LoadingSpinner className="w-4 h-4 mr-2" />
        )}
        {children}
        {renderIcon('right')}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
