import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';

interface ProtectedRouteProps {
  allowedRoles: Array<'admin' | 'manager' | 'user'>;
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles, children }) => {
  const currentUser = authService.getCurrentUser();
  const location = useLocation();

  if (!currentUser) {
    // Not logged in
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!allowedRoles.includes(currentUser.role)) {
    // Logged in, but does not have the required role
    // Redirect them to a page they have access to, or an unauthorized page
    // For simplicity, we'll send them to the home page.
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
