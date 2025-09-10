/**
 * Enhanced Auth Store
 * Zustand store для аутентификации с поддержкой MFA и enhanced security
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  EnhancedEmployee,
  AuthStoreState,
  EmployeeRole
} from './types';
import { enhancedAuthApi } from '../services/api/enhancedAuthApi';

interface LoginRequest {
  username: string;
  password: string;
  mfa_code?: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  employee: EnhancedEmployee;
  mfa_required: boolean;
  expires_in: number;
}

interface AuthStoreActions {
  // Authentication
  login: (credentials: LoginRequest) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  
  // MFA
  setupMFA: () => Promise<{ secret: string; qr_code: string }>;
  verifyMFA: (code: string) => Promise<boolean>;
  disableMFA: (password: string) => Promise<void>;
  
  // Session management
  updateLastActivity: () => void;
  checkSession: () => boolean;
  
  // Profile management
  updateProfile: (data: Partial<EnhancedEmployee>) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  
  // State management
  setEmployee: (employee: EnhancedEmployee | null) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  
  // Permissions
  hasPermission: (permission: string) => boolean;
  hasRole: (role: EmployeeRole) => boolean;
  canAccessResource: (resource: string, action: string) => boolean;
}

type AuthStore = AuthStoreState & AuthStoreActions;

const initialState: AuthStoreState = {
  // Authentication
  isAuthenticated: false,
  currentEmployee: null,
  token: null,
  refreshToken: null,
  
  // Session
  sessionExpiry: null,
  lastActivity: Date.now(),
  
  // UI State
  isLoading: false,
  error: null,
  
  // MFA
  mfaRequired: false,
  mfaSecret: null,
};

// Role hierarchy for permission checking
const ROLE_HIERARCHY: Record<EmployeeRole, number> = {
  [EmployeeRole.OWNER]: 100,
  [EmployeeRole.ADMIN]: 80,
  [EmployeeRole.MANAGER]: 60,
  [EmployeeRole.PHOTOGRAPHER]: 40,
  [EmployeeRole.STAFF]: 20,
  [EmployeeRole.ASSISTANT]: 10,
};

// Permission mappings
const ROLE_PERMISSIONS: Record<EmployeeRole, string[]> = {
  [EmployeeRole.OWNER]: ['*'], // All permissions
  [EmployeeRole.ADMIN]: [
    'bookings:read', 'bookings:write', 'bookings:delete',
    'employees:read', 'employees:write', 'employees:delete',
    'settings:read', 'settings:write',
    'analytics:read', 'gallery:write'
  ],
  [EmployeeRole.MANAGER]: [
    'bookings:read', 'bookings:write',
    'employees:read',
    'settings:read',
    'analytics:read'
  ],
  [EmployeeRole.PHOTOGRAPHER]: [
    'bookings:read', 'bookings:write',
    'gallery:write'
  ],
  [EmployeeRole.STAFF]: [
    'bookings:read'
  ],
  [EmployeeRole.ASSISTANT]: [
    'bookings:read'
  ],
};

export const useAuthStore = create<AuthStore>()(
  devtools(
    immer(
      persist(
        (set, get) => ({
          ...initialState,

          // Authentication
          login: async (credentials: LoginRequest): Promise<LoginResponse> => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const response = await enhancedAuthApi.login(credentials);
              
              set((state) => {
                state.isAuthenticated = true;
                state.currentEmployee = response.employee;
                state.token = response.access_token;
                state.refreshToken = response.refresh_token;
                state.sessionExpiry = Date.now() + (response.expires_in * 1000);
                state.lastActivity = Date.now();
                state.mfaRequired = response.mfa_required;
                state.isLoading = false;
              });

              return response;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка аутентификации';
                state.isLoading = false;
              });
              throw error;
            }
          },

          logout: async () => {
            set((state) => {
              state.isLoading = true;
            });

            try {
              const { token } = get();
              if (token) {
                await enhancedAuthApi.logout(token);
              }
            } catch (error) {
              console.warn('Logout API call failed:', error);
            } finally {
              set((state) => {
                state.isAuthenticated = false;
                state.currentEmployee = null;
                state.token = null;
                state.refreshToken = null;
                state.sessionExpiry = null;
                state.mfaRequired = false;
                state.mfaSecret = null;
                state.error = null;
                state.isLoading = false;
              });
            }
          },

          refreshToken: async (): Promise<boolean> => {
            const { refreshToken: currentRefreshToken } = get();
            
            if (!currentRefreshToken) {
              return false;
            }

            try {
              const response = await enhancedAuthApi.refreshToken(currentRefreshToken);
              
              set((state) => {
                state.token = response.access_token;
                state.refreshToken = response.refresh_token;
                state.sessionExpiry = Date.now() + (response.expires_in * 1000);
                state.lastActivity = Date.now();
              });

              return true;
            } catch (error) {
              // Refresh failed, logout user
              get().logout();
              return false;
            }
          },

          // MFA
          setupMFA: async (): Promise<{ secret: string; qr_code: string }> => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const response = await enhancedAuthApi.setupMFA();
              
              set((state) => {
                state.mfaSecret = response.secret;
                state.isLoading = false;
              });

              return response;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка настройки MFA';
                state.isLoading = false;
              });
              throw error;
            }
          },

          verifyMFA: async (code: string): Promise<boolean> => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const result = await enhancedAuthApi.verifyMFA(code);
              
              set((state) => {
                if (result && state.currentEmployee) {
                  state.currentEmployee.mfa_enabled = true;
                  state.mfaRequired = false;
                }
                state.isLoading = false;
              });

              return result;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Неверный код MFA';
                state.isLoading = false;
              });
              return false;
            }
          },

          disableMFA: async (password: string) => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              await enhancedAuthApi.disableMFA(password);
              
              set((state) => {
                if (state.currentEmployee) {
                  state.currentEmployee.mfa_enabled = false;
                }
                state.mfaSecret = null;
                state.isLoading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка отключения MFA';
                state.isLoading = false;
              });
              throw error;
            }
          },

          // Session management
          updateLastActivity: () => {
            set((state) => {
              state.lastActivity = Date.now();
            });
          },

          checkSession: (): boolean => {
            const { sessionExpiry, isAuthenticated } = get();
            
            if (!isAuthenticated || !sessionExpiry) {
              return false;
            }

            const now = Date.now();
            const sessionValid = now < sessionExpiry;
            
            if (!sessionValid) {
              get().logout();
              return false;
            }

            // Auto-refresh if session expires in less than 5 minutes
            const fiveMinutes = 5 * 60 * 1000;
            if (sessionExpiry - now < fiveMinutes) {
              get().refreshToken();
            }

            return true;
          },

          // Profile management
          updateProfile: async (data: Partial<EnhancedEmployee>) => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const updatedEmployee = await enhancedAuthApi.updateProfile(data);
              
              set((state) => {
                state.currentEmployee = updatedEmployee;
                state.isLoading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка обновления профиля';
                state.isLoading = false;
              });
              throw error;
            }
          },

          changePassword: async (currentPassword: string, newPassword: string) => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              await enhancedAuthApi.changePassword(currentPassword, newPassword);
              
              set((state) => {
                state.isLoading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка смены пароля';
                state.isLoading = false;
              });
              throw error;
            }
          },

          // State management
          setEmployee: (employee: EnhancedEmployee | null) => {
            set((state) => {
              state.currentEmployee = employee;
            });
          },

          setError: (error: string | null) => {
            set((state) => {
              state.error = error;
            });
          },

          clearError: () => {
            set((state) => {
              state.error = null;
            });
          },

          setLoading: (loading: boolean) => {
            set((state) => {
              state.isLoading = loading;
            });
          },

          // Permissions
          hasPermission: (permission: string): boolean => {
            const { currentEmployee } = get();
            
            if (!currentEmployee) {
              return false;
            }

            const rolePermissions = ROLE_PERMISSIONS[currentEmployee.role];
            
            // Owner has all permissions
            if (rolePermissions.includes('*')) {
              return true;
            }

            return rolePermissions.includes(permission);
          },

          hasRole: (role: EmployeeRole): boolean => {
            const { currentEmployee } = get();
            return currentEmployee?.role === role;
          },

          canAccessResource: (resource: string, action: string): boolean => {
            const permission = `${resource}:${action}`;
            return get().hasPermission(permission);
          },
        }),
        {
          name: 'auth-store',
          partialize: (state) => ({
            token: state.token,
            refreshToken: state.refreshToken,
            currentEmployee: state.currentEmployee,
            sessionExpiry: state.sessionExpiry,
            isAuthenticated: state.isAuthenticated,
          }),
        }
      )
    ),
    { name: 'AuthStore' }
  )
);

export default useAuthStore;
