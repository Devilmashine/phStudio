export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  full_name: string;
  created_at: string;
  last_login: string | null;
}

export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
}

export interface Booking {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  status: BookingStatus;
  client_name: string;
  client_phone: string;
  client_email: string;
  total_price: number;
  notes: string;
  created_at: string;
  updated_at: string;
}

export enum BookingStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  CANCELLED = 'cancelled',
  COMPLETED = 'completed',
}

export interface Statistics {
  total_bookings: number;
  total_hours: number;
  total_revenue: number;
  time_distribution: {
    morning: number;
    afternoon: number;
    evening: number;
  };
  average_duration: number;
  success_rate: number;
  cancellation_rate: number;
  popular_slots: Array<{
    slot: string;
    count: number;
  }>;
  new_vs_returning: {
    new: number;
    returning: number;
  };
  notification_stats: {
    total_sent: number;
    total_pending: number;
  };
} 