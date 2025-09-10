/**
 * Recent Bookings Component
 * Компонент для отображения последних бронирований
 */

import React from 'react';
import { 
  ClockIcon,
  UserIcon,
  PhoneIcon
} from '@heroicons/react/24/outline';
import { EnhancedBooking, BookingState } from '../../../stores/types';
import LoadingSpinner from '../../common/LoadingSpinner';

interface RecentBookingsProps {
  bookings: EnhancedBooking[];
  loading: boolean;
  onRefresh: () => void;
}

const stateColors = {
  [BookingState.DRAFT]: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  [BookingState.PENDING]: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  [BookingState.CONFIRMED]: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  [BookingState.IN_PROGRESS]: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
  [BookingState.COMPLETED]: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  [BookingState.CANCELLED]: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  [BookingState.NO_SHOW]: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
};

const stateLabels = {
  [BookingState.DRAFT]: 'Черновик',
  [BookingState.PENDING]: 'Ожидает',
  [BookingState.CONFIRMED]: 'Подтверждено',
  [BookingState.IN_PROGRESS]: 'В процессе',
  [BookingState.COMPLETED]: 'Завершено',
  [BookingState.CANCELLED]: 'Отменено',
  [BookingState.NO_SHOW]: 'Не явился',
};

export const RecentBookings: React.FC<RecentBookingsProps> = ({
  bookings,
  loading,
  onRefresh
}) => {
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Последние бронирования
          </h3>
          <button
            onClick={onRefresh}
            disabled={loading}
            className="inline-flex items-center px-3 py-1 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? (
              <LoadingSpinner className="w-4 h-4" />
            ) : (
              'Обновить'
            )}
          </button>
        </div>
      </div>

      <div className="flow-root">
        {loading && bookings.length === 0 ? (
          <div className="flex justify-center items-center py-12">
            <LoadingSpinner className="w-6 h-6 mr-2" />
            <span className="text-gray-600 dark:text-gray-400">Загрузка...</span>
          </div>
        ) : bookings.length === 0 ? (
          <div className="text-center py-12">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              Нет бронирований
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Бронирования появятся здесь по мере их создания.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {bookings.map((booking) => (
              <li key={booking.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center min-w-0 flex-1">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
                        <UserIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      </div>
                    </div>
                    
                    <div className="ml-4 min-w-0 flex-1">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {booking.client_name}
                          </p>
                          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                            <PhoneIcon className="w-4 h-4 mr-1" />
                            {booking.client_phone}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${stateColors[booking.state]}`}>
                            {stateLabels[booking.state]}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <ClockIcon className="w-4 h-4 mr-1" />
                        <span>
                          {formatDate(booking.booking_date)} в {formatTime(booking.start_time)}
                        </span>
                        <span className="mx-2">•</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {booking.total_price.toLocaleString('ru-RU')} ₽
                        </span>
                      </div>
                      
                      {booking.special_requirements && (
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 truncate">
                          {booking.special_requirements}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {bookings.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-700/50 px-6 py-3">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Показано {bookings.length} последних бронирований
          </div>
        </div>
      )}
    </div>
  );
};

export default RecentBookings;
