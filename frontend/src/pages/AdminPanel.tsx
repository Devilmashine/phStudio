import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import AdminLayout from '../components/admin/AdminLayout';

const AdminPanel: React.FC = () => {
  return (
    <AdminLayout>
      <Outlet />
    </AdminLayout>
  );
};

export default AdminPanel;
