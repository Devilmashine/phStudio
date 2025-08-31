export interface BookingState {
  DRAFT = "draft",
  PENDING = "pending",
  CONFIRMED = "confirmed",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  NO_SHOW = "no_show"
}

export interface BookingSource {
  WEBSITE = "website",
  PHONE = "phone",
  WALK_IN = "walk_in",
  ADMIN = "admin"
}

export interface BookingCreate {
  client_name: string;
  client_phone: string;
  client_email?: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  space_type: string;
  duration_hours: number;
  base_price: number;
  total_price: number;
  special_requirements?: string;
  source?: BookingSource;
}

export interface BookingUpdateState {
  new_state: BookingState;
  notes?: string;
}

export interface BookingResponse {
  id: number;
  booking_reference: string;
  client_name: string;
  client_phone: string;
  client_email?: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  state: BookingState;
  space_type: string;
  duration_hours: number;
  base_price: number;
  total_price: number;
  special_requirements?: string;
  source: BookingSource;
  created_at: string;
  updated_at: string;
  state_history: Array<{
    from_state: string;
    to_state: string;
    timestamp: string;
    employee_id?: number;
    notes?: string;
  }>;
}