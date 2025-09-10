/**
 * Booking Chart Component
 * Компонент для отображения графика бронирований
 */

import React from 'react';
import { EnhancedBooking, BookingState } from '../../../stores/types';
import LoadingSpinner from '../../common/LoadingSpinner';
import { ChartBarIcon } from '@heroicons/react/24/outline';

interface BookingChartProps {
  bookings: EnhancedBooking[];
  loading: boolean;
}

export const BookingChart: React.FC<BookingChartProps> = ({
  bookings,
  loading
}) => {
  // Generate chart data for the last 7 days
  const generateChartData = () => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toISOString().split('T')[0];
    });

    return last7Days.map(date => {
      const dayBookings = bookings.filter(booking => booking.booking_date === date);
      const completed = dayBookings.filter(b => b.state === BookingState.COMPLETED).length;
      const total = dayBookings.length;
      
      return {
        date,
        total,
        completed,
        label: new Date(date).toLocaleDateString('ru-RU', { 
          weekday: 'short', 
          day: '2-digit' 
        })
      };
    });
  };

  const chartData = generateChartData();
  const maxValue = Math.max(...chartData.map(d => d.total), 1);

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            График бронирований
          </h3>
        </div>
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner className="w-6 h-6 mr-2" />
          <span className="text-gray-600 dark:text-gray-400">Загрузка графика...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            График бронирований
          </h3>
          <ChartBarIcon className="w-5 h-5 text-gray-400" />
        </div>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Последние 7 дней
        </p>
      </div>

      <div className="p-6">
        {chartData.every(d => d.total === 0) ? (
          <div className="text-center py-12">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              Нет данных для графика
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Данные появятся после создания бронирований.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Chart bars */}
            <div className="flex items-end justify-between h-32 space-x-2">
              {chartData.map((data, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  <div className="w-full flex flex-col justify-end h-24">
                    {/* Completed bookings bar */}
                    <div 
                      className="w-full bg-green-500 rounded-t"
                      style={{ 
                        height: `${(data.completed / maxValue) * 100}%`,
                        minHeight: data.completed > 0 ? '4px' : '0px'
                      }}
                      title={`Завершено: ${data.completed}`}
                    />
                    {/* Total bookings bar */}
                    <div 
                      className="w-full bg-blue-500 rounded-t"
                      style={{ 
                        height: `${((data.total - data.completed) / maxValue) * 100}%`,
                        minHeight: (data.total - data.completed) > 0 ? '4px' : '0px'
                      }}
                      title={`Остальные: ${data.total - data.completed}`}
                    />
                  </div>
                  
                  {/* Date label */}
                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
                    {data.label}
                  </div>
                  
                  {/* Value label */}
                  <div className="text-xs font-medium text-gray-900 dark:text-white">
                    {data.total}
                  </div>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center space-x-6 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded mr-2" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Всего бронирований
                </span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded mr-2" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Завершенные
                </span>
              </div>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {chartData.reduce((sum, d) => sum + d.total, 0)}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Всего за неделю
                </div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-green-600 dark:text-green-400">
                  {chartData.reduce((sum, d) => sum + d.completed, 0)}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Завершено
                </div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-indigo-600 dark:text-indigo-400">
                  {Math.round(
                    (chartData.reduce((sum, d) => sum + d.completed, 0) / 
                     Math.max(chartData.reduce((sum, d) => sum + d.total, 0), 1)) * 100
                  )}%
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Процент завершения
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BookingChart;
