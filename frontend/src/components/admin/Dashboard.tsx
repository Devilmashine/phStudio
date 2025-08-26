import React from 'react';

// Mock data for dashboard
const stats = [
  { name: 'Всего бронирований', value: '1,234', change: '+12%', changeType: 'positive' },
  { name: 'Доход за месяц', value: '120,560 ₽', change: '+8%', changeType: 'positive' },
  { name: 'Активные пользователи', value: '567', change: '+3%', changeType: 'positive' },
  { name: 'Отказы', value: '23', change: '-2%', changeType: 'negative' },
];

const recentBookings = [
  { id: 1, client: 'Иван Петров', date: '2023-06-15', time: '14:00', status: 'Подтверждено' },
  { id: 2, client: 'Мария Сидорова', date: '2023-06-15', time: '16:00', status: 'Ожидает' },
  { id: 3, client: 'Алексей Иванов', date: '2023-06-16', time: '10:00', status: 'Подтверждено' },
  { id: 4, client: 'Елена Козлова', date: '2023-06-16', time: '12:00', status: 'Отменено' },
];

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
          Дашборд
        </h2>
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
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Последние бронирования</h3>
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700">
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {recentBookings.map((booking) => (
                <li key={booking.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-indigo-600 dark:text-indigo-400 truncate">
                        {booking.client}
                      </p>
                      <div className="ml-2 flex-shrink-0 flex">
                        <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                          {booking.status}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                          {booking.date} в {booking.time}
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Chart placeholder */}
        <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Статистика бронирований</h3>
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700">
            <div className="p-6 h-80 flex items-center justify-center bg-gray-50 dark:bg-gray-700">
              <div className="text-center">
                <div className="text-gray-500 dark:text-gray-400">График бронирований по дням</div>
                <div className="mt-4 text-sm text-gray-400 dark:text-gray-500">
                  Визуализация данных будет здесь
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;