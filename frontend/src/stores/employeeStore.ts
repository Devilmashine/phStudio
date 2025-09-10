/**
 * Enhanced Employee Store
 * Zustand store для управления сотрудниками
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  EnhancedEmployee,
  EmployeeStoreState,
  EmployeeFilters,
  EmployeeRole,
  EmployeeStatus
} from './types';
import { enhancedEmployeeApi } from '../services/api/enhancedEmployeeApi';

interface CreateEmployeeRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: EmployeeRole;
  phone?: string;
  department?: string;
  position?: string;
}

interface UpdateEmployeeRequest {
  full_name?: string;
  email?: string;
  role?: EmployeeRole;
  status?: EmployeeStatus;
  phone?: string;
  department?: string;
  position?: string;
}

interface EmployeeStoreActions {
  // Data fetching
  fetchEmployees: (filters?: EmployeeFilters, page?: number) => Promise<void>;
  fetchEmployee: (id: number) => Promise<void>;
  refreshEmployees: () => Promise<void>;
  
  // CRUD operations
  createEmployee: (data: CreateEmployeeRequest) => Promise<EnhancedEmployee>;
  updateEmployee: (id: number, data: UpdateEmployeeRequest) => Promise<EnhancedEmployee>;
  deleteEmployee: (id: number) => Promise<void>;
  
  // Employee management
  activateEmployee: (id: number) => Promise<EnhancedEmployee>;
  deactivateEmployee: (id: number) => Promise<EnhancedEmployee>;
  suspendEmployee: (id: number, reason?: string) => Promise<EnhancedEmployee>;
  terminateEmployee: (id: number, reason?: string) => Promise<EnhancedEmployee>;
  resetPassword: (id: number) => Promise<{ temporary_password: string }>;
  unlockAccount: (id: number) => Promise<void>;
  
  // State management
  setSelectedEmployee: (employee: EnhancedEmployee | null) => void;
  setFilters: (filters: Partial<EmployeeFilters>) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  
  // UI state
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Cache management
  invalidateCache: () => void;
  updateEmployeeInCache: (employee: EnhancedEmployee) => void;
  removeEmployeeFromCache: (id: number) => void;
}

type EmployeeStore = EmployeeStoreState & EmployeeStoreActions;

const initialState: EmployeeStoreState = {
  // Data
  employees: [],
  selectedEmployee: null,
  employeeFilters: {},
  
  // UI State
  loading: false,
  error: null,
  isCreating: false,
  isUpdating: false,
  
  // Pagination
  currentPage: 1,
  totalPages: 1,
  totalItems: 0,
  itemsPerPage: 20,
};

export const useEmployeeStore = create<EmployeeStore>()(
  devtools(
    immer(
      persist(
        (set, get) => ({
          ...initialState,

          // Data fetching
          fetchEmployees: async (filters?: EmployeeFilters, page?: number) => {
            set((state) => {
              state.loading = true;
              state.error = null;
            });

            try {
              const currentPage = page || get().currentPage;
              const currentFilters = filters || get().employeeFilters;
              
              const response = await enhancedEmployeeApi.getEmployees({
                ...currentFilters,
                page: currentPage,
                per_page: get().itemsPerPage,
              });

              set((state) => {
                state.employees = response.items;
                state.currentPage = response.page;
                state.totalPages = response.pages;
                state.totalItems = response.total;
                state.employeeFilters = currentFilters;
                state.loading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при загрузке сотрудников';
                state.loading = false;
              });
            }
          },

          fetchEmployee: async (id: number) => {
            set((state) => {
              state.loading = true;
              state.error = null;
            });

            try {
              const employee = await enhancedEmployeeApi.getEmployee(id);
              
              set((state) => {
                state.selectedEmployee = employee;
                
                // Update employee in cache if it exists
                const existingIndex = state.employees.findIndex(e => e.id === id);
                if (existingIndex !== -1) {
                  state.employees[existingIndex] = employee;
                }
                
                state.loading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при загрузке сотрудника';
                state.loading = false;
              });
            }
          },

          refreshEmployees: async () => {
            const { employeeFilters, currentPage } = get();
            await get().fetchEmployees(employeeFilters, currentPage);
          },

          // CRUD operations
          createEmployee: async (data: CreateEmployeeRequest): Promise<EnhancedEmployee> => {
            set((state) => {
              state.isCreating = true;
              state.error = null;
            });

            try {
              const employee = await enhancedEmployeeApi.createEmployee(data);
              
              set((state) => {
                // Add to beginning of list
                state.employees.unshift(employee);
                state.totalItems += 1;
                state.isCreating = false;
              });

              return employee;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при создании сотрудника';
                state.isCreating = false;
              });
              throw error;
            }
          },

          updateEmployee: async (id: number, data: UpdateEmployeeRequest): Promise<EnhancedEmployee> => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              const employee = await enhancedEmployeeApi.updateEmployee(id, data);
              
              set((state) => {
                // Update in cache
                const index = state.employees.findIndex(e => e.id === id);
                if (index !== -1) {
                  state.employees[index] = employee;
                }
                
                // Update selected employee if it's the same
                if (state.selectedEmployee?.id === id) {
                  state.selectedEmployee = employee;
                }
                
                state.isUpdating = false;
              });

              return employee;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при обновлении сотрудника';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          deleteEmployee: async (id: number) => {
            set((state) => {
              state.loading = true;
              state.error = null;
            });

            try {
              await enhancedEmployeeApi.deleteEmployee(id);
              
              set((state) => {
                state.employees = state.employees.filter(e => e.id !== id);
                state.totalItems -= 1;
                
                if (state.selectedEmployee?.id === id) {
                  state.selectedEmployee = null;
                }
                
                state.loading = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при удалении сотрудника';
                state.loading = false;
              });
              throw error;
            }
          },

          // Employee management
          activateEmployee: async (id: number): Promise<EnhancedEmployee> => {
            return get().updateEmployee(id, { status: EmployeeStatus.ACTIVE });
          },

          deactivateEmployee: async (id: number): Promise<EnhancedEmployee> => {
            return get().updateEmployee(id, { status: EmployeeStatus.INACTIVE });
          },

          suspendEmployee: async (id: number, reason?: string): Promise<EnhancedEmployee> => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              const employee = await enhancedEmployeeApi.suspendEmployee(id, reason);
              
              set((state) => {
                // Update in cache
                const index = state.employees.findIndex(e => e.id === id);
                if (index !== -1) {
                  state.employees[index] = employee;
                }
                
                // Update selected employee if it's the same
                if (state.selectedEmployee?.id === id) {
                  state.selectedEmployee = employee;
                }
                
                state.isUpdating = false;
              });

              return employee;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при приостановке сотрудника';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          terminateEmployee: async (id: number, reason?: string): Promise<EnhancedEmployee> => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              const employee = await enhancedEmployeeApi.terminateEmployee(id, reason);
              
              set((state) => {
                // Update in cache
                const index = state.employees.findIndex(e => e.id === id);
                if (index !== -1) {
                  state.employees[index] = employee;
                }
                
                // Update selected employee if it's the same
                if (state.selectedEmployee?.id === id) {
                  state.selectedEmployee = employee;
                }
                
                state.isUpdating = false;
              });

              return employee;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при увольнении сотрудника';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          resetPassword: async (id: number): Promise<{ temporary_password: string }> => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              const result = await enhancedEmployeeApi.resetPassword(id);
              
              set((state) => {
                state.isUpdating = false;
              });

              return result;
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при сбросе пароля';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          unlockAccount: async (id: number) => {
            set((state) => {
              state.isUpdating = true;
              state.error = null;
            });

            try {
              await enhancedEmployeeApi.unlockAccount(id);
              
              // Refresh employee data
              await get().fetchEmployee(id);
              
              set((state) => {
                state.isUpdating = false;
              });
            } catch (error: any) {
              set((state) => {
                state.error = error.message || 'Ошибка при разблокировке аккаунта';
                state.isUpdating = false;
              });
              throw error;
            }
          },

          // State management
          setSelectedEmployee: (employee: EnhancedEmployee | null) => {
            set((state) => {
              state.selectedEmployee = employee;
            });
          },

          setFilters: (filters: Partial<EmployeeFilters>) => {
            set((state) => {
              state.employeeFilters = { ...state.employeeFilters, ...filters };
              state.currentPage = 1; // Reset to first page when filters change
            });
          },

          clearFilters: () => {
            set((state) => {
              state.employeeFilters = {};
              state.currentPage = 1;
            });
          },

          setPage: (page: number) => {
            set((state) => {
              state.currentPage = page;
            });
          },

          // UI state
          setLoading: (loading: boolean) => {
            set((state) => {
              state.loading = loading;
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

          // Cache management
          invalidateCache: () => {
            set((state) => {
              state.employees = [];
              state.selectedEmployee = null;
            });
          },

          updateEmployeeInCache: (employee: EnhancedEmployee) => {
            set((state) => {
              const index = state.employees.findIndex(e => e.id === employee.id);
              if (index !== -1) {
                state.employees[index] = employee;
              }
              
              if (state.selectedEmployee?.id === employee.id) {
                state.selectedEmployee = employee;
              }
            });
          },

          removeEmployeeFromCache: (id: number) => {
            set((state) => {
              state.employees = state.employees.filter(e => e.id !== id);
              
              if (state.selectedEmployee?.id === id) {
                state.selectedEmployee = null;
              }
            });
          },
        }),
        {
          name: 'employee-store',
          partialize: (state) => ({
            employeeFilters: state.employeeFilters,
            currentPage: state.currentPage,
            itemsPerPage: state.itemsPerPage,
          }),
        }
      )
    ),
    { name: 'EmployeeStore' }
  )
);

export default useEmployeeStore;
