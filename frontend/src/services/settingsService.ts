import axios from 'axios';
import api from './api';

export interface StudioSettings {
  id: number;
  name: string;
  contacts: string;
  prices: string;
  work_days: string[];
  work_start_time: string;
  work_end_time: string;
  base_price_per_hour: number;
  weekend_price_multiplier: number;
  telegram_notifications_enabled: boolean;
  email_notifications_enabled: boolean;
  holidays?: string[];
  min_booking_duration: number;
  max_booking_duration: number;
  advance_booking_days: number;
  created_at?: string;
  updated_at?: string;
}

export type StudioSettingsPayload = Omit<StudioSettings, 'id' | 'created_at' | 'updated_at'>;

const basePath = '/settings';

export async function fetchSettings(): Promise<StudioSettings | null> {
  try {
    const { data } = await api.get<StudioSettings>(`${basePath}/`);
    return data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function createSettings(payload: StudioSettingsPayload): Promise<StudioSettings> {
  const { data } = await api.post<StudioSettings>(`${basePath}/`, payload);
  return data;
}

export async function updateSettings(payload: StudioSettingsPayload): Promise<StudioSettings> {
  const { data } = await api.put<StudioSettings>(`${basePath}/`, payload);
  return data;
}