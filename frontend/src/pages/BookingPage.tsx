import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBookingService } from '../services/bookingService';
import { formatTime, getTimeSlots, isTimeSlotAvailable } from '../utils/dateUtils';

const BookingPage: React.FC = () => {
  const navigate = useNavigate();
  const { getBookings, createBooking, loading, error } = useBookingService();
  const [bookings, setBookings] = useState<any[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [formData, setFormData] = useState({
    client_name: '',
    client_phone: '',
    client_email: '',
    notes: '',
  });

  useEffect(() => {
    const fetchBookings = async () => {
      try {
        const data = await getBookings();
        setBookings(data);
      } catch (err) {
        console.error('Ошибка при загрузке бронирований:', err);
      }
    };

    fetchBookings();
  }, []); // Убрана зависимость getBookings

  const calculateTotalPrice = (selectedTime: string): number => {
    const pricePerHour = 2500; // Стоимость за час, можно вынести в конфигурацию
    return pricePerHour; // В данном случае расчет фиксирован, но можно усложнить при необходимости
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedDate || !selectedTime) {
      alert('Пожалуйста, выберите дату и время');
      return;
    }

    if (!formData.client_name) {
      alert('Имя клиента обязательно');
      return;
    }
    if (!formData.client_phone) {
      alert('Телефон клиента обязателен');
      return;
    }
    const totalPrice = calculateTotalPrice(selectedTime);
    if (totalPrice <= 0) {
      alert('Цена должна быть больше 0');
      return;
    }

    try {
      const [hours, minutes] = selectedTime.split(':');
      const endTime = `${(parseInt(hours) + 1).toString().padStart(2, '0')}:${minutes}`;

      await createBooking({
        date: selectedDate,
        start_time: selectedTime,
        end_time: endTime,
        total_price: totalPrice,
        ...formData,
      });

      navigate('/booking/success');
    } catch (err) {
      console.error('Ошибка при создании бронирования:', err);
    }
  };

  const availableTimeSlots = getTimeSlots('09:00', '21:00').filter(slot =>
    isTimeSlotAvailable(slot, bookings)
  );

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">Форма бронирования</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
            Дата
          </label>
          <input
            id="date"
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
            min={new Date().toISOString().split('T')[0]}
            required
          />
        </div>

        <div>
          <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
            Время
          </label>
          <select
            id="time"
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
            required
          >
            <option value="">Выберите время</option>
            {availableTimeSlots.map((slot) => (
              <option key={slot} value={slot}>
                {formatTime(slot)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Имя
          </label>
          <input
            id="name"
            type="text"
            value={formData.client_name}
            onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
            className="w-full px-4 py-2 border rounded-md"
            required
          />
        </div>

        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
            Телефон
          </label>
          <input
            id="phone"
            type="tel"
            value={formData.client_phone}
            onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
            className="w-full px-4 py-2 border rounded-md"
            required
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={formData.client_email}
            onChange={(e) => setFormData({ ...formData, client_email: e.target.value })}
            className="w-full px-4 py-2 border rounded-md"
            required
          />
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
            Дополнительная информация
          </label>
          <textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="w-full px-4 py-2 border rounded-md"
            rows={4}
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
        >
          {loading ? 'Забронировать' : 'Забронировать'}
        </button>
      </form>
    </div>
  );
};

export default BookingPage;