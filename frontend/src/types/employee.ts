export interface EmployeeRole {
  OWNER = "owner",
  ADMIN = "admin",
  MANAGER = "manager"
}

export interface EmployeeStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  TERMINATED = "terminated"
}

export interface EmployeeCreate {
  full_name: string;
  username: string;
  email: string;
  password: string;
  role: EmployeeRole;
  phone?: string;
  department?: string;
}

export interface EmployeeUpdate {
  full_name?: string;
  email?: string;
  role?: EmployeeRole;
  phone?: string;
  department?: string;
  status?: EmployeeStatus;
}

export interface EmployeeResponse {
  id: number;
  employee_id: string;
  full_name: string;
  username: string;
  email: string;
  role: EmployeeRole;
  phone?: string;
  department?: string;
  status: EmployeeStatus;
  hire_date?: string;
  created_at: string;
  updated_at: string;
}