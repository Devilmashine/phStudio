import { TELEGRAM_CONFIG } from './config';
import { BookingData } from '../../types';
import { getBookingById } from '../booking';

const sendTelegramMessage = async (chatId: string, message: string) => {
  const url = `https://api.telegram.org/bot${TELEGRAM_CONFIG.botToken}/sendMessage`;

  await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      chat_id: chatId,
      text: message,
      parse_mode: 'HTML',
    }),
  });
};

/**
 * Отправляет уведомление администратору о новом бронировании.
 */
export async function sendAdminNotification(booking: BookingData) {
  const message = `
🎯 <b>Новое бронирование!</b>

👤 Клиент: ${booking.name}
📱 Телефон: ${booking.phone}
📅 Дата: ${booking.date}
🕒 Время: ${booking.times.join(', ')}
💰 Сумма: ${booking.totalPrice} ₽

${booking.id ? `
<b>Нажмите /confirm_${booking.id} для подтверждения брони</b>
<b>Нажмите /cancel_${booking.id} для отмены брони</b>
` : ''}
`;

  await sendTelegramMessage(TELEGRAM_CONFIG.adminChatId!, message);
}

/**
 * Отправляет уведомление клиенту о подтверждении бронирования.
 */
export async function sendClientNotification(booking: BookingData) {
  if (!booking.clientChatId) {
    console.warn('No client chat ID provided for booking notification');
    return;
  }

  const message = `
✨ <b>Бронирование подтверждено!</b>

Детали вашей брони:
📅 Дата: ${booking.date}
🕒 Время: ${booking.times.join(', ')}
💰 Сумма: ${booking.totalPrice} ₽

Ждем вас в студии!
`;

  await sendTelegramMessage(booking.clientChatId, message);
}

/**
 * Отправляет уведомление клиенту об отмене бронирования.
 */
export async function sendCancellationNotification(booking: BookingData) {
  if (!booking.clientChatId) {
    console.warn('No client chat ID provided for cancellation notification');
    return;
  }

  const message = `
🚫 <b>Бронирование отменено!</b>

Ваше бронирование на ${booking.date} в ${booking.times.join(', ')} было отменено.

Если у вас есть вопросы, свяжитесь с нами.
`;

  await sendTelegramMessage(booking.clientChatId, message);
}

/**
 * Обрабатывает команду подтверждения бронирования.
 */
export async function handleConfirmation(bookingId: string) {
  const booking = await getBookingById(bookingId);
  
  if (!booking) {
    console.error(`Booking ${bookingId} not found`);
    return;
  }

  booking.status = 'confirmed';
  await sendClientNotification(booking);
}

/**
 * Обрабатывает команду отмены бронирования.
 */
export async function handleCancellation(bookingId: string) {
  const booking = await getBookingById(bookingId);
  
  if (!booking) {
    console.error(`Booking ${bookingId} not found`);
    return;
  }

  booking.status = 'cancelled';
  await sendCancellationNotification(booking);
}