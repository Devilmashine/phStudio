/**
 * Enhanced Employee API Client
 * Интеграция с новым enhanced employee backend API
 */

import api from '../api';
import {
  EnhancedEmployee,
  EmployeeFilters,
  EmployeeRole,
  EmployeeStatus,
  PaginatedResponse,
  ApiResponse
} from '../../stores/types';

interface EmployeeQueryParams extends EmployeeFilters {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

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

class EnhancedEmployeeApi {
  private readonly basePath = '/v2/employees';

  /**
   * Get paginated list of employees with filters
   */
  async getEmployees(params?: EmployeeQueryParams): Promise<PaginatedResponse<EnhancedEmployee>> {
    const response = await api.get<PaginatedResponse<EnhancedEmployee>>(this.basePath, {
      params: this.cleanParams(params),
    });
    return response.data;
  }

  /**
   * Get single employee by ID
   */
  async getEmployee(id: number): Promise<EnhancedEmployee> {
    const response = await api.get<ApiResponse<EnhancedEmployee>>(`${this.basePath}/${id}`);
    return response.data.data;
  }

  /**
   * Create new employee
   */
  async createEmployee(data: CreateEmployeeRequest): Promise<EnhancedEmployee> {
    const response = await api.post<ApiResponse<EnhancedEmployee>>(this.basePath, data);
    return response.data.data;
  }

  /**
   * Update existing employee
   */
  async updateEmployee(id: number, data: UpdateEmployeeRequest): Promise<EnhancedEmployee> {
    const response = await api.put<ApiResponse<EnhancedEmployee>>(`${this.basePath}/${id}`, data);
    return response.data.data;
  }

  /**
   * Delete employee (soft delete)
   */
  async deleteEmployee(id: number): Promise<void> {
    await api.delete(`${this.basePath}/${id}`);
  }

  /**
   * Suspend employee account
   */
  async suspendEmployee(id: number, reason?: string): Promise<EnhancedEmployee> {
    const response = await api.post<ApiResponse<EnhancedEmployee>>(
      `${this.basePath}/${id}/suspend`,
      { reason }
    );
    return response.data.data;
  }

  /**
   * Terminate employee
   */
  async terminateEmployee(id: number, reason?: string): Promise<EnhancedEmployee> {
    const response = await api.post<ApiResponse<EnhancedEmployee>>(
      `${this.basePath}/${id}/terminate`,
      { reason }
    );
    return response.data.data;
  }

  /**
   * Reset employee password
   */
  async resetPassword(id: number): Promise<{ temporary_password: string }> {
    const response = await api.post<ApiResponse<{ temporary_password: string }>>(
      `${this.basePath}/${id}/reset-password`
    );
    return response.data.data;
  }

  /**
   * Unlock employee account
   */
  async unlockAccount(id: number): Promise<void> {
    await api.post(`${this.basePath}/${id}/unlock`);
  }

  /**
   * Force password change for employee
   */
  async forcePasswordChange(id: number): Promise<void> {
    await api.post(`${this.basePath}/${id}/force-password-change`);
  }

  /**
   * Get employee permissions
   */
  async getEmployeePermissions(id: number): Promise<string[]> {
    const response = await api.get<ApiResponse<{ permissions: string[] }>>(
      `${this.basePath}/${id}/permissions`
    );
    return response.data.data.permissions;
  }

  /**
   * Update employee permissions
   */
  async updateEmployeePermissions(id: number, permissions: string[]): Promise<void> {
    await api.put(`${this.basePath}/${id}/permissions`, {
      permissions,
    });
  }

  /**
   * Get employee activity log
   */
  async getEmployeeActivity(id: number, params?: {
    page?: number;
    per_page?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<{
    id: string;
    action: string;
    description: string;
    ip_address: string;
    user_agent: string;
    timestamp: string;
    metadata: Record<string, any>;
  }>> {
    const response = await api.get<PaginatedResponse<any>>(
      `${this.basePath}/${id}/activity`,
      { params }
    );
    return response.data;
  }

  /**
   * Get employee statistics
   */
  async getEmployeeStats(): Promise<{
    total_employees: number;
    active_employees: number;
    inactive_employees: number;
    suspended_employees: number;
    terminated_employees: number;
    by_role: Array<{ role: EmployeeRole; count: number }>;
    by_department: Array<{ department: string; count: number }>;
    recent_logins: Array<{
      employee_id: number;
      full_name: string;
      last_login: string;
    }>;
  }> {
    const response = await api.get<ApiResponse<any>>(`${this.basePath}/stats`);
    return response.data.data;
  }

  /**
   * Bulk update employees
   */
  async bulkUpdateEmployees(data: {
    employee_ids: number[];
    updates: Partial<UpdateEmployeeRequest>;
  }): Promise<EnhancedEmployee[]> {
    const response = await api.post<ApiResponse<EnhancedEmployee[]>>(
      `${this.basePath}/bulk-update`,
      data
    );
    return response.data.data;
  }

  /**
   * Export employees to CSV
   */
  async exportEmployees(params?: EmployeeQueryParams): Promise<Blob> {
    const response = await api.get(`${this.basePath}/export`, {
      params: this.cleanParams(params),
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Import employees from CSV
   */
  async importEmployees(file: File): Promise<{
    imported: number;
    errors: Array<{ row: number; error: string }>;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<ApiResponse<any>>(
      `${this.basePath}/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data;
  }

  /**
   * Get employee departments
   */
  async getDepartments(): Promise<string[]> {
    const response = await api.get<ApiResponse<{ departments: string[] }>>(
      `${this.basePath}/departments`
    );
    return response.data.data.departments;
  }

  /**
   * Get employee positions
   */
  async getPositions(): Promise<string[]> {
    const response = await api.get<ApiResponse<{ positions: string[] }>>(
      `${this.basePath}/positions`
    );
    return response.data.data.positions;
  }

  /**
   * Search employees by query
   */
  async searchEmployees(query: string, params?: {
    limit?: number;
    include_inactive?: boolean;
  }): Promise<EnhancedEmployee[]> {
    const response = await api.get<ApiResponse<EnhancedEmployee[]>>(
      `${this.basePath}/search`,
      {
        params: {
          q: query,
          ...params,
        },
      }
    );
    return response.data.data;
  }

  /**
   * Clean undefined/null parameters
   */
  private cleanParams(params?: any): any {
    if (!params) return {};
    
    const cleaned: any = {};
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        cleaned[key] = params[key];
      }
    });
    
    return cleaned;
  }
}

// Export singleton instance
export const enhancedEmployeeApi = new EnhancedEmployeeApi();
export default enhancedEmployeeApi;
