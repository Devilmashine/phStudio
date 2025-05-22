import { useApi } from '../hooks/useApi';

export interface Booking {
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
  created_at: string;
  updated_at: string;
}

export interface CreateBookingDto {
  date: string;
  start_time: string;
  end_time: string;
  client_name: string;
  client_phone: string;
  client_email: string;
  total_price: number; // Добавлено поле для передачи итоговой суммы
  notes?: string;
}

export const useBookingService = () => {
  const api = useApi<Booking>();

  const getBookings = async () => {
    return api.fetchData('/bookings');
  };

  const getBooking = async (id: number) => {
    return api.fetchData(`/bookings/${id}`);
  };

  const createBooking = async (data: CreateBookingDto) => {
    const transformedData = {
      date: data.date,
      times: [data.start_time, data.end_time],
      name: data.client_name,
      phone: data.client_phone,
      totalPrice: data.total_price,
      notes: data.notes,
    };
    return api.fetchData('/bookings', {
      method: 'POST',
      body: JSON.stringify(transformedData),
    });
  };

  const updateBookingStatus = async (id: number, status: string) => {
    return api.fetchData(`/bookings/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  };

  const deleteBooking = async (id: number) => {
    return api.fetchData(`/bookings/${id}`, {
      method: 'DELETE',
    });
  };

  return {
    ...api,
    getBookings,
    getBooking,
    createBooking,
    updateBookingStatus,
    deleteBooking,
  };
};