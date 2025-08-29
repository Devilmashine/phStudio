import React from 'react';

interface ResponsiveHelperProps {
  children: React.ReactNode;
  className?: string;
}

// Helper component for consistent responsive design
export const ResponsiveCard: React.FC<ResponsiveHelperProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden ${className}`}>
      {children}
    </div>
  );
};

// Helper component for responsive grid layouts
export const ResponsiveGrid: React.FC<{ children: React.ReactNode; cols?: number }> = ({ 
  children, 
  cols = 1 
}) => {
  const gridClasses = `grid gap-6 ${
    cols === 1 ? 'grid-cols-1' :
    cols === 2 ? 'grid-cols-1 md:grid-cols-2' :
    cols === 3 ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' :
    cols === 4 ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4' :
    'grid-cols-1'
  }`;
  
  return (
    <div className={gridClasses}>
      {children}
    </div>
  );
};

// Helper component for responsive buttons
export const ResponsiveButton: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger' }
> = ({ 
  children, 
  variant = 'primary', 
  className = '', 
  ...props 
}) => {
  const baseClasses = "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variantClasses = {
    primary: "text-white bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500",
    secondary: "text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-indigo-500 dark:text-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:hover:bg-gray-600",
    danger: "text-white bg-red-600 hover:bg-red-700 focus:ring-red-500"
  };
  
  return (
    <button
      type="button"
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};