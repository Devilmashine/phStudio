import React from 'react';
import { format } from 'date-fns';

interface BookingDetailsProps {
  selectedDate: Date | null;
  selectedTimes: string[];
  totalPrice: number;
}

const BookingDetails = React.memo(({ selectedDate, selectedTimes, totalPrice }: BookingDetailsProps) => {
  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <h4 className="font-medium text-gray-900 mb-2">Детали бронирования</h4>
      <div className="space-y-2 text-sm text-gray-600">
        {selectedDate && (
          <p>Дата: {format(selectedDate, 'dd.MM.yyyy')}</p>
        )}
        {selectedTimes.length > 0 && (
          <p>Время: {selectedTimes.join(', ')}</p>
        )}
        <p className="text-lg font-bold text-indigo-600">
          Итого: {totalPrice} ₽
        </p>
      </div>
    </div>
  );
});

export default BookingDetails;