// Типы для ролей и прав доступа в админ-панели фотостудии

export type Permission =
  | 'view_dashboard'
  | 'manage_bookings'
  | 'view_bookings'
  | 'manage_reviews'
  | 'view_reviews'
  | 'export_data'
  | 'manage_users'
  | 'manage_roles'
  | 'view_logs'
  | 'manage_services';

export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

export const PERMISSIONS: { key: Permission; label: string }[] = [
  { key: 'view_dashboard', label: 'Просмотр аналитики' },
  { key: 'manage_bookings', label: 'Управление бронированиями' },
  { key: 'view_bookings', label: 'Просмотр бронирований' },
  { key: 'manage_reviews', label: 'Управление отзывами' },
  { key: 'view_reviews', label: 'Просмотр отзывов' },
  { key: 'export_data', label: 'Экспорт данных' },
  { key: 'manage_users', label: 'Управление пользователями' },
  { key: 'manage_roles', label: 'Управление ролями и правами' },
  { key: 'view_logs', label: 'Просмотр логов' },
  { key: 'manage_services', label: 'Управление услугами и прайсом' },
]; 