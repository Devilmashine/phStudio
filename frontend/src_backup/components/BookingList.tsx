import React, { useState, useEffect, useCallback } from 'react';
import bookingService from '../services/bookingService';

// Assuming a BookingStatus enum/type exists
enum BookingStatus {
  Pending = 'pending',
  Confirmed = 'confirmed',
  Cancelled = 'cancelled',
}

interface Booking {
  id: number;
  client_name: string;
  client_phone: string;
  start_time: string;
  end_time: string;
  status: BookingStatus;
  // Add other fields as necessary
}

const BookingList: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBookings = useCallback(async () => {
    try {
      setLoading(true);
      const response = await bookingService.getAllBookings();
      setBookings(response.data);
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

  const handleStatusUpdate = async (bookingId: number, status: BookingStatus) => {
    try {
      await bookingService.updateBookingStatus(bookingId, status);
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
                <td className="py-2 px-4 border-b">{booking.status}</td>
                <td className="py-2 px-4 border-b text-center">
                  {booking.status === BookingStatus.Pending && (
                    <button
                      onClick={() => handleStatusUpdate(booking.id, BookingStatus.Confirmed)}
                      className="text-green-600 hover:underline mr-2"
                    >
                      Confirm
                    </button>
                  )}
                  {booking.status !== BookingStatus.Cancelled && (
                    <button
                      onClick={() => handleStatusUpdate(booking.id, BookingStatus.Cancelled)}
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
