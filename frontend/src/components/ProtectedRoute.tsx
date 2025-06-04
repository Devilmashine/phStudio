import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  allowedRoles?: string[];
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles = ['admin'], children }) => {
  const navigate = useNavigate();
  const { tryRefresh } = useAuth();
  useEffect(() => {
    const token = localStorage.getItem('token');
    const exp = localStorage.getItem('token_exp');
    const role = localStorage.getItem('role');
    if (!token || !exp || !role || (allowedRoles && !allowedRoles.includes(role)) || Date.now() > parseInt(exp, 10)) {
      tryRefresh().then(success => {
        if (!success) navigate('/login', { replace: true });
      });
    }
  }, [navigate, tryRefresh, allowedRoles]);
  return <>{children}</>;
};

export default ProtectedRoute;
