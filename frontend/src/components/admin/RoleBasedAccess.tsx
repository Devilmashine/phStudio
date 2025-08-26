import React, { ReactNode } from 'react';

interface RoleBasedAccessProps {
  allowedRoles: string[];
  userRole: string;
  children: ReactNode;
  fallback?: ReactNode;
}

const RoleBasedAccess: React.FC<RoleBasedAccessProps> = ({ 
  allowedRoles, 
  userRole, 
  children,
  fallback = null
}) => {
  const hasAccess = allowedRoles.includes(userRole);
  
  return hasAccess ? <>{children}</> : <>{fallback}</>;
};

export default RoleBasedAccess;