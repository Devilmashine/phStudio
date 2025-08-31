import { EmployeeResponse, EmployeeCreate, EmployeeUpdate } from '../types/employee';

const API_BASE_URL = '/api/v2';

export class EmployeeService {
  static async createEmployee(employeeData: EmployeeCreate): Promise<EmployeeResponse> {
    const response = await fetch(`${API_BASE_URL}/employees`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employeeData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create employee: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getEmployees(
    skip: number = 0,
    limit: number = 100,
    role?: string,
    status?: string
  ): Promise<{ employees: EmployeeResponse[]; total: number }> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    
    if (role) params.append('role', role);
    if (status) params.append('status', status);
    
    const response = await fetch(`${API_BASE_URL}/employees?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch employees: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getEmployee(employeeId: number): Promise<EmployeeResponse> {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Employee not found');
      }
      throw new Error(`Failed to fetch employee: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async updateEmployee(
    employeeId: number,
    updateData: EmployeeUpdate
  ): Promise<EmployeeResponse> {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update employee: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async deleteEmployee(employeeId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete employee: ${response.statusText}`);
    }
  }
}