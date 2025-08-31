import React, { useState, useEffect, useCallback } from 'react';
import { BookingService } from '../services/bookingService';
import { BookingResponse, BookingState } from '../types/booking';

const BookingList: React.FC = () => {
  const [bookings, setBookings] = useState<BookingResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBookings = useCallback(async () => {
    try {
      setLoading(true);
      const response = await BookingService.getBookings();
      setBookings(response.bookings);
    } catch (err) {
      setError('Failed to fetch bookings.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  const handleStatusUpdate = async (bookingId: number, newState: BookingState) => {
    try {
      await BookingService.updateBookingState(bookingId, newState);
      fetchBookings(); // Refresh list after update
    } catch (err) {
      setError('Failed to update booking status.');
      console.error(err);
    }
  };

  if (loading) {
    return <div>Loading bookings...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">All Bookings</h1>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border">
          <thead className="bg-gray-200">
            <tr>
              <th className="py-2 px-4 border-b">ID</th>
              <th className="py-2 px-4 border-b">Client Name</th>
              <th className="py-2 px-4 border-b">Phone</th>
              <th className="py-2 px-4 border-b">Start Time</th>
              <th className="py-2 px-4 border-b">End Time</th>
              <th className="py-2 px-4 border-b">Status</th>
              <th className="py-2 px-4 border-b">Actions</th>
            </tr>
          </thead>
          <tbody>
            {bookings.map((booking) => (
              <tr key={booking.id}>
                <td className="py-2 px-4 border-b text-center">{booking.id}</td>
                <td className="py-2 px-4 border-b">{booking.client_name}</td>
                <td className="py-2 px-4 border-b">{booking.client_phone}</td>
                <td className="py-2 px-4 border-b">{new Date(booking.start_time).toLocaleString()}</td>
                <td className="py-2 px-4 border-b">{new Date(booking.end_time).toLocaleString()}</td>
                <td className="py-2 px-4 border-b">{booking.state}</td>
                <td className="py-2 px-4 border-b text-center">
                  {booking.state === 'pending' && (
                    <button
                      onClick={() => handleStatusUpdate(booking.id, 'confirmed')}
                      className="text-green-600 hover:underline mr-2"
                    >
                      Confirm
                    </button>
                  )}
                  {booking.state !== 'cancelled' && (
                    <button
                      onClick={() => handleStatusUpdate(booking.id, 'cancelled')}
                      className="text-red-600 hover:underline"
                    >
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BookingList;