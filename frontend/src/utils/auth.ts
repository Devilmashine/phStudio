import { Role } from '../types/roles';

export function getCurrentUserRole(roles: Role[]): Role | undefined {
  const userRoleName = localStorage.getItem('user_role');
  return roles.find(r => r.name === userRoleName);
} 