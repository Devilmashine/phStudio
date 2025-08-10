import api from './api';

const API_URL = '/api/bookings';

const getAllBookings = () => {
  return api.get(API_URL);
};

const updateBookingStatus = (bookingId, status) => {
  return api.patch(`${API_URL}/${bookingId}/status`, { status });
};

const bookingService = {
  getAllBookings,
  updateBookingStatus,
};

export default bookingService;
