import { Permission, Role } from '../types/roles';

export function hasPermission(role: Role | undefined, perm: Permission): boolean {
  return !!role && role.permissions.includes(perm);
} 