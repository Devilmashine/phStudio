import React, { useState, useEffect, useCallback } from 'react';
import { getDashboardStatsApi, getRecentBookingsApi } from '../../services/booking/api';
import { websocketService } from '../../services/websocket';
import { BookingChart } from '../../components/enhanced/AdminDashboard/BookingChart';
import { BookingState, SpaceType, PaymentStatus, BookingSource, BookingPriority } from '../../stores/types';

// Define TypeScript interfaces
interface Stat {
  name: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative';
}

interface RecentBooking {
  id: number;
  client_name: string;
  date: string;
  start_time: string;
  status: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stat[]>([]);
  const [recentBookings, setRecentBookings] = useState<RecentBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: ''
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Format date as YYYY-MM-DD
  const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  // Set default date range to last 30 days
  useEffect(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - 30);
    
    setDateRange({
      start: formatDate(start),
      end: formatDate(end)
    });
  }, []);

  const fetchData = useCallback(async (startDate?: string, endDate?: string) => {
    try {
      setLoading(true);
      const [statsData, bookingsData] = await Promise.all([
        getDashboardStatsApi(startDate, endDate),
        getRecentBookingsApi(10, startDate, endDate)
      ]);

      // Transform stats data for display
      const transformedStats: Stat[] = [
        { 
          name: 'Всего бронирований', 
          value: statsData.total_bookings.toString(), 
          change: '+12%', 
          changeType: 'positive' 
        },
        { 
          name: 'Доход за период', 
          value: `${statsData.total_revenue.toLocaleString('ru-RU')} ₽`, 
          change: '+8%', 
          changeType: 'positive' 
        },
        { 
          name: 'Активные пользователи', 
          value: statsData.unique_clients.toString(), 
          change: '+3%', 
          changeType: 'positive' 
        },
        { 
          name: 'Отказы', 
          value: statsData.cancelled_bookings.toString(), 
          change: '-2%', 
          changeType: 'negative' 
        },
      ];

      setStats(transformedStats);
      setRecentBookings(bookingsData);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Не удалось загрузить данные дашборда');
    } finally {
      setLoading(false);
    }
  }, []);

  // Handle real-time updates
  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();

    // Subscribe to booking updates
    const unsubscribe = websocketService.subscribe('booking_update', (data) => {
      console.log('Received booking update:', data);
      // Refresh data when a booking is updated
      handleRefresh();
    });

    // Cleanup
    return () => {
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (dateRange.start && dateRange.end) {
      fetchData(dateRange.start, dateRange.end);
    }
  }, [dateRange, fetchData]);

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setDateRange(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleApplyFilter = () => {
    if (dateRange.start && dateRange.end) {
      fetchData(dateRange.start, dateRange.end);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    if (dateRange.start && dateRange.end) {
      await fetchData(dateRange.start, dateRange.end);
    }
    setIsRefreshing(false);
  };

  if (loading && (!stats.length || !recentBookings.length)) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error && (!stats.length || !recentBookings.length)) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Ошибка! </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
          Дашборд
        </h2>
        
        {/* Controls */}
        <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row sm:space-x-2 space-y-2 sm:space-y-0">
          <div>
            <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              От
            </label>
            <input
              type="date"
              id="start-date"
              name="start"
              value={dateRange.start}
              onChange={handleDateChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          <div>
            <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              До
            </label>
            <input
              type="date"
              id="end-date"
              name="end"
              value={dateRange.end}
              onChange={handleDateChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          <div className="flex items-end space-x-2">
            <button
              onClick={handleApplyFilter}
              disabled={isRefreshing}
              className="h-9 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              Применить
            </button>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="h-9 inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
            >
              {isRefreshing ? (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : null}
              {isRefreshing ? 'Обновление...' : 'Обновить'}
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                  <div className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">{stat.name}</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900 dark:text-white">{stat.value}</div>
                      <div
                        className={`ml-2 flex items-baseline text-sm font-semibold ${
                          stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {stat.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent bookings */}
        <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Последние бронирования</h3>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {websocketService.isConnectedStatus() ? (
                <span className="inline-flex items-center">
                  <span className="h-2 w-2 rounded-full bg-green-400 mr-1"></span>
                  Обновления в реальном времени
                </span>
              ) : (
                <span className="inline-flex items-center">
                  <span className="h-2 w-2 rounded-full bg-yellow-400 mr-1"></span>
                  Нет подключения
                </span>
              )}
            </div>
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700">
            {loading ? (
              <div className="px-4 py-5 sm:px-6">
                <div className="animate-spin rounded-full h-8 w-8 mx-auto border-b-2 border-indigo-500"></div>
              </div>
            ) : error ? (
              <div className="px-4 py-5 sm:px-6 text-red-500">{error}</div>
            ) : (
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {recentBookings.length > 0 ? (
                  recentBookings.map((booking) => (
                    <li key={booking.id}>
                      <div className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-indigo-600 dark:text-indigo-400 truncate">
                            {booking.client_name}
                          </p>
                          <div className="ml-2 flex-shrink-0 flex">
                            <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              booking.status === 'confirmed' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                                : booking.status === 'pending'
                                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
                            }`}>
                              {booking.status === 'confirmed' ? 'Подтверждено' : 
                               booking.status === 'pending' ? 'Ожидает' : 'Отменено'}
                            </p>
                          </div>
                        </div>
                        <div className="mt-2 sm:flex sm:justify-between">
                          <div className="sm:flex">
                            <p className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                              {booking.date} в {new Date(booking.start_time).toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})}
                            </p>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))
                ) : (
                  <li>
                    <div className="px-4 py-4 sm:px-6 text-center text-gray-500 dark:text-gray-400">
                      Нет бронирований за выбранный период
                    </div>
                  </li>
                )}
              </ul>
            )}
          </div>
        </div>

        {/* Booking Chart */}
        <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Статистика бронирований</h3>
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <BookingChart 
                bookings={recentBookings.map(booking => ({
                  id: booking.id,
                  booking_reference: `BK-${booking.id}`,
                  client_name: booking.client_name,
                  client_phone: '', // Not available in RecentBooking
                  client_phone_normalized: '', // Not available in RecentBooking
                  client_email: '', // Not available in RecentBooking
                  booking_date: booking.date,
                  start_time: booking.start_time,
                  end_time: booking.start_time, // Simplified
                  duration_hours: 1, // Default value
                  state: booking.status as BookingState, // Type assertion
                  state_history: [], // Empty array as we don't have this data
                  space_type: SpaceType.MAIN_STUDIO, // Default value
                  equipment_requested: [], // Empty array
                  special_requirements: '', // Empty string
                  base_price: 0, // Default value
                  equipment_price: 0, // Default value
                  discount_amount: 0, // Default value
                  total_price: 0, // Default value
                  payment_status: PaymentStatus.PENDING, // Default value
                  source: BookingSource.WEBSITE, // Default value
                  notes: '', // Empty string
                  internal_notes: '', // Empty string
                  priority: BookingPriority.NORMAL, // Default value
                  created_at: booking.start_time,
                  updated_at: booking.start_time,
                  version: 1 // Default value
                }))} 
                loading={loading} 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;