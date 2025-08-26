import { BookingData } from '../../types';

export const generateEventDescription = (booking: BookingData): string => {
  return `
    Клиент: ${booking.name}
    Телефон: ${booking.phone}
    Стоимость: ${booking.totalPrice} ₽
  `.trim();
};