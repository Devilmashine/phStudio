import React from 'react';

interface ErrorDisplayProps {
  errors: string[];
}

const ErrorDisplay = React.memo(({ errors }: ErrorDisplayProps) => {
  if (errors.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <p className="text-sm font-medium text-red-800 mb-2">
        Пожалуйста, исправьте следующие ошибки:
      </p>
      <ul className="list-disc list-inside text-sm text-red-700">
        {errors.map((error, index) => (
          <li key={index}>{error}</li>
        ))}
      </ul>
    </div>
  );
});

export default ErrorDisplay;