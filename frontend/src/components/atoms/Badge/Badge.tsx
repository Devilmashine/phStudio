/**
 * Badge Atom Component
 * Базовый компонент бейджа следуя Atomic Design
 */

import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  removable?: boolean;
  onRemove?: () => void;
  className?: string;
}

const variantClasses = {
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  primary: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
  secondary: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
  success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  danger: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
};

const dotColors = {
  default: 'bg-gray-400',
  primary: 'bg-indigo-400',
  secondary: 'bg-gray-400',
  success: 'bg-green-400',
  warning: 'bg-yellow-400',
  danger: 'bg-red-400',
  info: 'bg-blue-400',
};

const sizeClasses = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-2.5 py-0.5 text-sm',
  lg: 'px-3 py-1 text-sm',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  removable = false,
  onRemove,
  className = '',
}) => {
  const baseClasses = `
    inline-flex items-center font-medium rounded-full
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <span className={baseClasses}>
      {dot && (
        <span 
          className={`
            w-2 h-2 rounded-full mr-1.5 flex-shrink-0
            ${dotColors[variant]}
          `} 
        />
      )}
      
      {children}
      
      {removable && onRemove && (
        <button
          onClick={onRemove}
          className="ml-1.5 flex-shrink-0 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-black hover:bg-opacity-10 focus:outline-none focus:bg-black focus:bg-opacity-10"
          type="button"
        >
          <span className="sr-only">Удалить</span>
          <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
            <path strokeLinecap="round" strokeWidth="1.5" d="m1 1 6 6m0-6L1 7" />
          </svg>
        </button>
      )}
    </span>
  );
};

export default Badge;
