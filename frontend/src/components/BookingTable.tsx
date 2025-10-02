import React, { useEffect, useMemo, useState } from 'react';
import { useBookingStore } from '../stores';
import { BookingState } from '../stores/types';
import LoadingSpinner from './common/LoadingSpinner';

const statusMap: Record<BookingState, { label: string; color: string }> = {
  [BookingState.DRAFT]: { label: 'Черновик', color: 'bg-gray-100 text-gray-800' },
  [BookingState.PENDING]: { label: 'Ожидает', color: 'bg-yellow-100 text-yellow-800' },
  [BookingState.CONFIRMED]: { label: 'Подтверждена', color: 'bg-blue-100 text-blue-800' },
  [BookingState.IN_PROGRESS]: { label: 'В процессе', color: 'bg-indigo-100 text-indigo-800' },
  [BookingState.COMPLETED]: { label: 'Завершена', color: 'bg-green-100 text-green-800' },
  [BookingState.CANCELLED]: { label: 'Отменена', color: 'bg-red-100 text-red-800' },
  [BookingState.NO_SHOW]: { label: 'Неявка', color: 'bg-red-100 text-red-800' },
  [BookingState.RESCHEDULED]: { label: 'Перенесена', color: 'bg-purple-100 text-purple-800' },
};

const stateLabelMap: Record<BookingState, string> = {
  [BookingState.DRAFT]: 'Черновики',
  [BookingState.PENDING]: 'Новые заявки',
  [BookingState.CONFIRMED]: 'Подтверждённые',
  [BookingState.IN_PROGRESS]: 'В работе',
  [BookingState.COMPLETED]: 'Завершённые',
  [BookingState.CANCELLED]: 'Отменённые',
  [BookingState.NO_SHOW]: 'Неявки',
  [BookingState.RESCHEDULED]: 'Перенесённые',
};

const BookingTable: React.FC = () => {
  const bookings = useBookingStore(state => state.bookings);
  const loading = useBookingStore(state => state.loading);
  const error = useBookingStore(state => state.error);
  const bookingFilters = useBookingStore(state => state.bookingFilters);
  const fetchBookings = useBookingStore(state => state.fetchBookings);
  const refreshBookings = useBookingStore(state => state.refreshBookings);
  const clearFilters = useBookingStore(state => state.clearFilters);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!bookings.length) {
      fetchBookings().catch(err => console.error('Failed to load bookings', err));
    }
  }, [bookings.length, fetchBookings]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshBookings();
    } finally {
      setRefreshing(false);
    }
  };

  const rows = useMemo(() => bookings.map(booking => ({
    id: booking.id,
    date: new Date(booking.booking_date).toLocaleDateString('ru-RU'),
    timeRange: `${new Date(booking.start_time).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })} — ${new Date(booking.end_time).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`,
    client: booking.client_name,
    phone: booking.client_phone,
    status: booking.state,
    amount: booking.total_price,
    people: booking.people_count,
  })), [bookings]);

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">Бронирования</h2>
        <button
          onClick={handleRefresh}
          className="px-3 py-2 text-sm border rounded hover:bg-gray-50 disabled:opacity-50"
          disabled={loading || refreshing}
        >
          {refreshing ? 'Обновление…' : 'Обновить'}
        </button>
      </div>

      {bookingFilters.state && (
        <div className="mb-4 flex items-center justify-between rounded-md border border-indigo-200 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/30 px-4 py-3 text-sm">
          <div className="flex items-center gap-2 text-indigo-800 dark:text-indigo-300">
            <span className="inline-flex h-2 w-2 rounded-full bg-indigo-500" />
            <span>
              Фильтр по стадии: <strong>{stateLabelMap[bookingFilters.state]}</strong>
            </span>
          </div>
          <button
            onClick={async () => {
              clearFilters();
              await fetchBookings();
            }}
            className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-300 dark:hover:text-indigo-200"
          >
            Сбросить
          </button>
        </div>
      )}

      {error && (
        <div className="mb-3 text-sm text-red-600">{typeof error === 'string' ? error : 'Ошибка загрузки бронирований'}</div>
      )}

      <div className="overflow-x-auto rounded-lg shadow-sm">
        <table className="min-w-full divide-y divide-gray-200" aria-label="Таблица бронирований">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Время</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Клиент</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Телефон</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сумма</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Гостей</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {loading && !rows.length ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400 text-sm" aria-live="polite">
                  <div className="flex flex-col items-center gap-2">
                    <LoadingSpinner className="w-6 h-6" />
                    <span>Загрузка бронирований…</span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400 text-sm" aria-live="polite">
                  Нет бронирований
                </td>
              </tr>
            ) : (
              rows.map(row => (
                <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap">{row.date}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{row.timeRange}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{row.client}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <a
                      href={`tel:${row.phone}`}
                      className="text-indigo-600 hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
                      aria-label={`Позвонить ${row.client}`}
                    >
                      {row.phone}
                    </a>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${statusMap[row.status].color}`}>
                      {statusMap[row.status].label}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">{row.amount.toLocaleString('ru-RU')} ₽</td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">{row.people}</td>
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
