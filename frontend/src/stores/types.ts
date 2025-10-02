/**
 * Enhanced Store Types for CRM Module
 * Следует архитектуре enhanced backend models
 */

// Enhanced Booking Types
export enum BookingState {
  DRAFT = "draft",
  PENDING = "pending",
  CONFIRMED = "confirmed",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  NO_SHOW = "no_show",
  RESCHEDULED = "rescheduled"
}

export enum SpaceType {
  MAIN_STUDIO = "main_studio",
  SMALL_STUDIO = "small_studio",
  OUTDOOR_AREA = "outdoor_area"
}

export enum PaymentStatus {
  PENDING = "pending",
  PARTIAL = "partial",
  PAID = "paid",
  REFUNDED = "refunded"
}

export enum BookingPriority {
  LOW = "low",
  NORMAL = "normal",
  HIGH = "high",
  URGENT = "urgent"
}

export enum BookingSource {
  WEBSITE = "website",
  PHONE = "phone",
  WALK_IN = "walk_in",
  ADMIN = "admin"
}

// Enhanced Employee Types
export enum EmployeeRole {
  OWNER = "owner",
  ADMIN = "admin",
  MANAGER = "manager",
  STAFF = "staff",
  PHOTOGRAPHER = "photographer",
  ASSISTANT = "assistant"
}

export enum EmployeeStatus {
  PENDING_ACTIVATION = "pending_activation",
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  TERMINATED = "terminated"
}

// Enhanced Booking Interface
export interface EnhancedBooking {
  id: number;
  booking_reference: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  duration_hours: number;
  state: BookingState;
  state_history: BookingStateHistory[];
  
  // Client Information
  client_name: string;
  client_phone: string;
  client_phone_normalized: string;
  client_email?: string;
  
  // Booking Details
  space_type: SpaceType;
  equipment_requested: string[];
  special_requirements?: string;
  
  // Pricing
  base_price: number;
  equipment_price: number;
  discount_amount: number;
  total_price: number;
  payment_status: PaymentStatus;
  
  // Metadata
  source: BookingSource;
  notes?: string;
  internal_notes?: string;
  priority: BookingPriority;
  
  // Audit Fields
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
  version: number;
}

export interface BookingStateHistory {
  from_state: BookingState;
  to_state: BookingState;
  timestamp: string;
  employee_id?: number;
  notes?: string;
  reason?: string;
}

// Enhanced Employee Interface
export interface EnhancedEmployee {
  id: number;
  employee_id: string;
  username: string;
  email: string;
  role: EmployeeRole;
  status: EmployeeStatus;
  
  // Profile Information
  full_name: string;
  phone?: string;
  department?: string;
  position?: string;
  hire_date?: string;
  timezone: string;
  language: string;
  
  // Security Information
  mfa_enabled: boolean;
  password_changed_at?: string;
  last_login?: string;
  last_activity?: string;
  failed_login_attempts: number;
  
  // Audit Fields
  created_at: string;
  updated_at: string;
  version: number;
}

// API Request/Response Types
export interface CreateBookingRequest {
  client_name: string;
  client_phone: string;
  client_email?: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  space_type: SpaceType;
  equipment_requested?: string[];
  special_requirements?: string;
  notes?: string;
  source?: BookingSource;
  priority?: BookingPriority;
}

export interface UpdateBookingRequest {
  client_name?: string;
  client_phone?: string;
  client_email?: string;
  start_time?: string;
  end_time?: string;
  space_type?: SpaceType;
  equipment_requested?: string[];
  special_requirements?: string;
  notes?: string;
  internal_notes?: string;
  priority?: BookingPriority;
}

export interface BookingStateTransitionRequest {
  new_state: BookingState;
  notes?: string;
  reason?: string;
}

// Store State Interfaces
export interface BookingStoreState {
  // Data
  bookings: EnhancedBooking[];
  selectedBooking: EnhancedBooking | null;
  bookingFilters: BookingFilters;
  
  // UI State
  loading: boolean;
  error: string | null;
  isCreating: boolean;
  isUpdating: boolean;
  
  // Pagination
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
}

export interface BookingFilters {
  dateFrom?: string;
  dateTo?: string;
  state?: BookingState;
  spaceType?: SpaceType;
  paymentStatus?: PaymentStatus;
  priority?: BookingPriority;
  source?: BookingSource;
  clientName?: string;
  phone?: string;
}

export interface EmployeeStoreState {
  // Data
  employees: EnhancedEmployee[];
  selectedEmployee: EnhancedEmployee | null;
  employeeFilters: EmployeeFilters;
  
  // UI State
  loading: boolean;
  error: string | null;
  isCreating: boolean;
  isUpdating: boolean;
  
  // Pagination
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
}

export interface EmployeeFilters {
  role?: EmployeeRole;
  status?: EmployeeStatus;
  department?: string;
  fullName?: string;
  email?: string;
}

export interface AuthStoreState {
  // Authentication
  isAuthenticated: boolean;
  currentEmployee: EnhancedEmployee | null;
  token: string | null;
  refreshToken: string | null;
  
  // Session
  sessionExpiry: number | null;
  lastActivity: number;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  
  // MFA
  mfaRequired: boolean;
  mfaSecret: string | null;
}

export interface UIStoreState {
  // Theme
  darkMode: boolean;
  
  // Layout
  sidebarCollapsed: boolean;
  
  // Notifications
  notifications: Notification[];
  
  // Modals
  modals: Record<string, boolean>;
  
  // Loading states
  globalLoading: boolean;
  
  // Real-time connection
  wsConnected: boolean;
  wsReconnecting: boolean;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: () => void;
  type?: 'primary' | 'secondary' | 'danger';
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, any>;
  field_errors?: Record<string, string[]>;
}

// CRM Dashboard Types
export interface CRMPipelineStage {
  state: BookingState;
  label: string;
  count: number;
  percentage: number;
}

export interface CRMEmployeePerformance {
  employee_id: number;
  full_name: string;
  role: string;
  completed_bookings: number;
  active_bookings: number;
  revenue_generated: number;
}

export interface CRMRevenuePoint {
  date: string;
  revenue: number;
  booking_count: number;
}

export interface CRMDashboardOverview {
  total_bookings: number;
  active_bookings: number;
  completed_today: number;
  revenue_30_days: number;
  avg_booking_value: number;
  occupancy_rate: number;
}

export interface CRMDashboardResponse {
  overview: CRMDashboardOverview;
  pipeline: CRMPipelineStage[];
  top_employees: CRMEmployeePerformance[];
  revenue_trend: CRMRevenuePoint[];
  generated_at: string;
}

// Event Types for Real-time Updates
export interface DomainEvent {
  event_type: string;
  aggregate_id: string;
  timestamp: string;
  metadata: {
    user_id?: number;
    ip_address?: string;
    user_agent?: string;
  };
}

export interface BookingCreatedEvent extends DomainEvent {
  event_type: 'BOOKING_CREATED';
  booking_id: number;
  reference: string;
  client_name: string;
  start_time: string;
  end_time: string;
}

export interface BookingStateChangedEvent extends DomainEvent {
  event_type: 'BOOKING_STATE_CHANGED';
  booking_id: number;
  reference: string;
  from_state: BookingState;
  to_state: BookingState;
  reason?: string;
}

export interface BookingUpdatedEvent extends DomainEvent {
  event_type: 'BOOKING_UPDATED';
  booking_id: number;
  reference: string;
  changes: Partial<EnhancedBooking>;
}

export interface BookingCancelledEvent extends DomainEvent {
  event_type: 'BOOKING_CANCELLED';
  booking_id: number;
  reference: string;
  reason?: string;
}
