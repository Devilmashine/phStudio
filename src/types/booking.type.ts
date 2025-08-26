export interface Booking {
  id?: string;
  name: string;
  phone: string;
  date: string;
  times: string[];
  totalPrice: number;
  service?: string;
  status: 'pending' | 'confirmed' | 'rejected';
}
