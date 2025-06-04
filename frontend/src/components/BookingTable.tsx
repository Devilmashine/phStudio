import React from 'react';

interface Booking {
  id: number;
  date: string;
  times: string[];
  name: string;
  phone: string;
  status: string;
  total_price: number;
  people_count: number;
}

const BookingTable: React.FC = () => {
  // Заглушка для таблицы бронирований
  return (
    <div>
      <h2 className="text-lg font-bold mb-2">Таблица бронирований (заглушка)</h2>
      <div className="text-gray-500">Тут будет таблица бронирований.</div>
    </div>
  );
};

export default BookingTable;
