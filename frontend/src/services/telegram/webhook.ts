import { TELEGRAM_CONFIG } from './config';
import { handleConfirmation, handleCancellation } from './notifications';

interface TelegramUpdate {
  message?: {
    text: string;
    chat: {
      id: number;
      type: string;
    };
  };
}

/**
 * Обрабатывает входящие сообщения от Telegram.
 */
export async function handleWebhookUpdate(update: TelegramUpdate) {
  if (!update.message || !update.message.text) return;

  const { text } = update.message;

  // Обработка команды подтверждения
  if (text.startsWith('/confirm_')) {
    const bookingId = text.split('_')[1];
    await handleConfirmation(bookingId);
  }

  // Обработка команды отмены
  if (text.startsWith('/cancel_')) {
    const bookingId = text.split('_')[1];
    await handleCancellation(bookingId);
  }
}

/**
 * Настраивает вебхук для Telegram бота.
 */
export async function setupWebhook() {
  const url = `${TELEGRAM_CONFIG.webhookUrl}/webhook`;
  const response = await fetch(
    `https://api.telegram.org/bot${TELEGRAM_CONFIG.botToken}/setWebhook`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url,
        allowed_updates: ['message'],
      }),
    }
  );

  if (!response.ok) {
    throw new Error('Failed to set up Telegram webhook');
  }

  return await response.json();
}