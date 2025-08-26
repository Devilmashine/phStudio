import React from 'react';
import { useNavigate } from 'react-router-dom';

const UserManagement: React.FC = () => {
  const navigate = useNavigate();
  
  // Redirect to the new admin user management
  React.useEffect(() => {
    navigate('/admin/users');
  }, [navigate]);

  return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );
};

export default UserManagement;
