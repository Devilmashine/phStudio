import React from 'react';

interface Booking {
  id: number;
  date: string;
  times: string[];
  name: string;
  phone: string;
  status: 'pending' | 'confirmed' | 'cancelled';
  total_price: number;
  people_count: number;
}

// Пример данных (можно заменить на реальные данные из API)
const bookings: Booking[] = [];

const statusMap: Record<Booking['status'], { label: string; color: string }> = {
  pending: { label: 'В ожидании', color: 'bg-yellow-100 text-yellow-800' },
  confirmed: { label: 'Подтверждена', color: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Отменена', color: 'bg-red-100 text-red-800' },
};

const BookingTable: React.FC = () => {
  return (
    <div className="w-full">
      <h2 className="text-lg font-bold mb-4">Бронирования</h2>
      <div className="overflow-x-auto rounded-lg shadow-sm">
        <table className="min-w-full divide-y divide-gray-200" aria-label="Таблица бронирований">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Время</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Телефон</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сумма</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Чел.</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {bookings.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400 text-sm" aria-live="polite">
                  Нет бронирований
                </td>
              </tr>
            ) : (
              bookings.map((b) => (
                <tr key={b.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap">{b.date}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{b.times.join(', ')}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{b.name}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <a href={`tel:${b.phone}`} className="text-indigo-600 hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded" aria-label={`Позвонить ${b.name}`}>{b.phone}</a>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${statusMap[b.status].color}`}>{statusMap[b.status].label}</span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">{b.total_price} ₽</td>
                  <td className="px-4 py-3 whitespace-nowrap">{b.people_count}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BookingTable;
