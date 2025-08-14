import React from 'react';
import BookingList from '../components/BookingList';

const ManagerPanel: React.FC = () => {
  return (
    <div className="p-4 sm:p-6 md:p-8">
      <h1 className="text-2xl font-bold mb-4">Manager Panel</h1>
      <p className="text-gray-600 mb-6">
        Here you can view and manage all client bookings.
      </p>
      <BookingList />
    </div>
  );
};

export default ManagerPanel;
