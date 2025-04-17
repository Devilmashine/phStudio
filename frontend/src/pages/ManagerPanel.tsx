import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Tab } from '@headlessui/react';

interface Booking {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  status: string;
  client_name: string;
  client_phone: string;
  client_email: string;
  total_price: number;
  notes: string;
}

const ManagerPanel: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    // Проверка авторизации и роли
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    fetchBookings();
  }, [navigate]);

  const fetchBookings = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/bookings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBookings(data);
      } else {
        throw new Error('Ошибка при получении бронирований');
      }
    } catch (error) {
      console.error('Ошибка:', error);
    }
  };

  const handleStatusChange = async (bookingId: number, newStatus: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/bookings/${bookingId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        setBookings(bookings.map(booking => 
          booking.id === bookingId ? { ...booking, status: newStatus } : booking
        ));
      } else {
        throw new Error('Ошибка при обновлении статуса');
      }
    } catch (error) {
      console.error('Ошибка:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Панель менеджера</h1>
          
          <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
            <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-8">
              <Tab className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                 ${selected
                   ? 'bg-white text-blue-700 shadow'
                   : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                 }`
              }>
                Бронирования
              </Tab>
              <Tab className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                 ${selected
                   ? 'bg-white text-blue-700 shadow'
                   : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                 }`
              }>
                Календарь
              </Tab>
              <Tab className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                 ${selected
                   ? 'bg-white text-blue-700 shadow'
                   : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                 }`
              }>
                Статистика
              </Tab>
            </Tab.List>

            <Tab.Panels>
              <Tab.Panel>
                <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Дата и время
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Клиент
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Контакты
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Статус
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Сумма
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {bookings.map((booking) => (
                        <tr key={booking.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(booking.date).toLocaleDateString()}<br/>
                            {booking.start_time} - {booking.end_time}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {booking.client_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {booking.client_phone}<br/>
                            {booking.client_email}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <select
                              value={booking.status}
                              onChange={(e) => handleStatusChange(booking.id, e.target.value)}
                              className="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            >
                              <option value="pending">Ожидает</option>
                              <option value="confirmed">Подтверждено</option>
                              <option value="cancelled">Отменено</option>
                              <option value="completed">Завершено</option>
                            </select>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {booking.total_price} ₽
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Tab.Panel>

              <Tab.Panel>
                <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Календарь</h3>
                  {/* Здесь будет календарь */}
                </div>
              </Tab.Panel>

              <Tab.Panel>
                <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Статистика</h3>
                  {/* Здесь будет компонент статистики */}
                </div>
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </div>
      </div>
    </div>
  );
};

export default ManagerPanel; 