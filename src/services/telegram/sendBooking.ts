import axios from 'axios';
import { BookingData } from '../../types';
import { createCalendarEvent } from '../calendar/api';

// Типы для Telegram
interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
}

interface TelegramMessage {
  chat: { id: string };
  message_id: number;
  phone: string;
  date: string;
  times: string[];
}

interface TelegramCallbackQuery {
  callback_data?: string;
  message: TelegramMessage;
  from: TelegramUser;
}

// Расширенный интерфейс для логирования действий
interface BookingActionLog {
  id: string; // Уникальный идентификатор лога
  timestamp: Date;
  bookingId?: string; 
  action: 'confirmed' | 'rejected' | 'created';
  performer: {
    id: number;
    firstName: string;
    lastName?: string;
    username?: string;
  };
  details: {
    calendarEventId?: string;
    reason?: string;
    additionalInfo?: Record<string, any>;
  };
  status: 'success' | 'error' | 'pending';
  errorMessage?: string;
}

export class TelegramNotificationService {
  private static instance: TelegramNotificationService;
  private bookingActionLogs: BookingActionLog[] = [];

  private constructor() {
    console.warn('🚨 TELEGRAM NOTIFICATION SERVICE INITIALIZATION 🚨');
  }

  public static getInstance(): TelegramNotificationService {
    if (!TelegramNotificationService.instance) {
      TelegramNotificationService.instance = new TelegramNotificationService();
    }
    return TelegramNotificationService.instance;
  }

  private formatBookingMessage(booking: BookingData): string {
    const formattedPhone = booking.phone.startsWith('+') 
      ? booking.phone 
      : `+${booking.phone}`;

    // Convert date to DD.MM.YYYY format
    const [year, month, day] = booking.date.split('-');
    const formattedDate = `${day}.${month}.${year}`;

    return `${formattedDate}
${booking.times.join(', ')}
${booking.name}
${formattedPhone}`;
  }

  private generateLogId(): string {
    return `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private logBookingAction(
    logEntry: Omit<BookingActionLog, 'id' | 'status'>, 
    status: BookingActionLog['status'] = 'success'
  ): BookingActionLog {
    const safeLogEntry = {
      ...logEntry,
      bookingId: logEntry.bookingId || this.generateLogId()
    };

    const logWithId: BookingActionLog = {
      id: this.generateLogId(),
      status,
      ...safeLogEntry
    };

    this.bookingActionLogs.push(logWithId);
    
    console.log(`📝 Booking Action Log [${logWithId.id}]: 
    Action: ${logWithId.action} 
    Booking ID: ${logWithId.bookingId || 'N/A'}
    Performer: ${logWithId.performer.firstName} ${logWithId.performer.lastName || ''}
    Status: ${logWithId.status}`);

    return logWithId;
  }

  // Метод для получения логов с возможностью фильтрации
  public getBookingActionLogs(filters: Partial<BookingActionLog> = {}): BookingActionLog[] {
    return this.bookingActionLogs.filter(log => 
      Object.entries(filters).every(([key, value]) => 
        key === 'bookingId' 
          ? log.bookingId === value 
          : log[key as keyof BookingActionLog] === value
      )
    );
  }

  // Метод для очистки логов
  public clearBookingActionLogs(olderThan?: Date): void {
    if (olderThan) {
      this.bookingActionLogs = this.bookingActionLogs.filter(
        log => log.timestamp > olderThan
      );
    } else {
      this.bookingActionLogs = [];
    }
    console.warn('🧹 Booking action logs cleared');
  }

  // Метод для получения последнего лога по бронированию
  public getLastBookingActionLog(bookingId: string): BookingActionLog | undefined {
    return this.bookingActionLogs
      .filter(log => log.bookingId === bookingId)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())[0];
  }

  public async sendBookingNotification(booking: BookingData): Promise<boolean> {
    const botToken = this.getBotToken();
    const adminChatId = this.getAdminChatId();

    if (!botToken || !adminChatId) {
      console.error('❌ TELEGRAM CONFIGURATION INCOMPLETE');
      return false;
    }

    try {
      await axios.post(
        `https://api.telegram.org/bot${botToken}/sendMessage`,
        {
          chat_id: adminChatId,
          text: this.formatBookingMessage(booking),
          parse_mode: 'HTML',
          reply_markup: {
            inline_keyboard: [
              [
                { 
                  text: '✅ Подтвердить', 
                  callback_data: `confirm_booking:${booking.id}` 
                },
                { 
                  text: '❌ Отклонить', 
                  callback_data: `reject_booking:${booking.id}` 
                }
              ]
            ]
          }
        },
        { timeout: 5000 }
      );

      // Логируем создание бронирования
      this.logBookingAction({
        timestamp: new Date(),
        bookingId: booking.id,
        action: 'created',
        performer: {
          id: 0,
          firstName: 'System',
          lastName: '',
          username: ''
        },
        details: {}
      });

      return true;
    } catch (error) {
      console.error('❌ TELEGRAM NOTIFICATION FAILED', error);
      return false;
    }
  }

  public async handleCallbackQuery(callbackQuery: TelegramCallbackQuery): Promise<void> {
    console.log('🔍 RECEIVED CALLBACK QUERY:', JSON.stringify(callbackQuery, null, 2));

    const { callback_data, message, from } = callbackQuery;

    if (!callback_data) {
      console.error('❌ NO CALLBACK DATA RECEIVED');
      return;
    }

    // Расширенное логирование
    console.log('🔑 Callback Data:', callback_data);
    console.log('👤 User:', JSON.stringify(from, null, 2));
    console.log('📨 Message:', JSON.stringify(message, null, 2));

    const [action, bookingId] = callback_data.split(':');

    console.log(`🚦 Action: ${action}, Booking ID: ${bookingId}`);

    try {
      switch (action) {
        case 'confirm_booking':
          console.log(`✅ Attempting to confirm booking: ${bookingId}`);
          await this.confirmBooking(bookingId, from, message);
          break;
        case 'reject_booking':
          console.log(`❌ Attempting to reject booking: ${bookingId}`);
          await this.rejectBooking(bookingId, from, message);
          break;
        default:
          console.warn(`❓ UNKNOWN CALLBACK ACTION: ${action}`);
      }
    } catch (error) {
      console.error('❌ CALLBACK QUERY PROCESSING FAILED', error);
      
      // Отправляем сообщение об ошибке в Telegram
      try {
        await this.sendErrorNotification(
          message.chat.id, 
          `Ошибка при обработке действия: ${action}\n${error instanceof Error ? error.message : 'Неизвестная ошибка'}`
        );
      } catch (notificationError) {
        console.error('❌ FAILED TO SEND ERROR NOTIFICATION', notificationError);
      }
    }
  }

  // Новый метод для отправки уведомлений об ошибках
  private async sendErrorNotification(chatId: string, errorMessage: string): Promise<void> {
    const botToken = this.getBotToken();
    
    if (!botToken) {
      console.error('❌ BOT TOKEN IS MISSING');
      return;
    }

    try {
      await axios.post(
        `https://api.telegram.org/bot${botToken}/sendMessage`,
        {
          chat_id: chatId,
          text: `⚠️ Произошла ошибка:\n${errorMessage}`,
          parse_mode: 'HTML'
        },
        { timeout: 5000 }
      );
    } catch (error) {
      console.error('❌ FAILED TO SEND ERROR MESSAGE', error);
    }
  }

  private async confirmBooking(bookingId: string, user: TelegramUser, message: TelegramMessage): Promise<void> {
    console.log(`🔔 Confirm Booking Method Called - Booking ID: ${bookingId}`);
    
    try {
      // Проверяем наличие всех необходимых данных
      if (!bookingId) {
        throw new Error('Booking ID is required');
      }

      // Создаем событие в Google Calendar
      const calendarEvent = await createCalendarEvent({
        summary: `Бронирование: ${user.first_name} ${user.last_name || ''}`,
        description: `Бронирование для ${user.first_name} ${user.last_name || ''}`,
        start: { 
          dateTime: new Date(message.date + 'T' + message.times[0]).toISOString() 
        },
        end: { 
          dateTime: new Date(message.date + 'T' + message.times[message.times.length - 1]).toISOString() 
        }
      });

      console.log(`📅 Calendar Event Created: ${calendarEvent.id}`);

      // Логируем действие
      const actionLog = this.logBookingAction({
        timestamp: new Date(),
        bookingId,
        action: 'confirmed',
        performer: {
          id: user.id,
          firstName: user.first_name,
          lastName: user.last_name,
          username: user.username
        },
        details: {
          calendarEventId: calendarEvent.id
        }
      });

      console.log(`📝 Action Log Created: ${actionLog.id}`);

      // Обновляем сообщение в Telegram
      await this.answerCallbackQuery(bookingId, '✅ Бронирование подтверждено', true);
      
      console.log(`📤 Callback Query Answered`);

      await this.editMessageText(
        message.chat.id, 
        message.message_id, 
        `${this.formatBookingMessage} \n\n✅ Подтверждено администратором ${user.first_name} ${user.last_name || ''}`
      );

      console.log(`📝 Message Edited`);

      // Отправляем сообщение администратору
      await this.sendAdminNotification(
        'Вы подтвердили бронирование - не забудьте сообщить клиенту об успешной записи!'
      );

      console.log(`📨 Admin Notification Sent`);

    } catch (error) {
      console.error('❌ BOOKING CONFIRMATION FAILED', error);
      
      // Отправляем подробное сообщение об ошибке
      await this.sendErrorNotification(
        message.chat.id, 
        `Ошибка подтверждения бронирования: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`
      );

      throw error; // Пробрасываем ошибку для глобального обработчика
    }
  }

  private async rejectBooking(bookingId: string, user: TelegramUser, message: TelegramMessage): Promise<void> {
    try {
      // Логируем действие
      this.logBookingAction({
        timestamp: new Date(),
        bookingId,
        action: 'rejected',
        performer: {
          id: user.id,
          firstName: user.first_name,
          lastName: user.last_name,
          username: user.username
        },
        details: {
          reason: 'Manual rejection by admin'
        }
      });

      // Обновляем сообщение в Telegram
      await this.answerCallbackQuery(bookingId, '❌ Бронирование отклонено', true);
      await this.editMessageText(
        message.chat.id, 
        message.message_id, 
        `${this.formatBookingMessage} \n\n❌ Отклонено администратором ${user.first_name} ${user.last_name || ''}`
      );

      // Отправляем сообщение администратору
      await this.sendAdminNotification(
        'Бронирование отменено, сообщите клиенту об этом и предложите выбрать другую дату'
      );
    } catch (error) {
      console.error('❌ BOOKING REJECTION FAILED', error);
    }
  }

  private async sendAdminNotification(message: string): Promise<void> {
    const botToken = this.getBotToken();
    const adminChatId = this.getAdminChatId();

    if (!botToken || !adminChatId) {
      console.error('❌ TELEGRAM CONFIGURATION INCOMPLETE');
      return;
    }

    try {
      await axios.post(
        `https://api.telegram.org/bot${botToken}/sendMessage`,
        {
          chat_id: adminChatId,
          text: message,
          parse_mode: 'HTML'
        },
        { timeout: 5000 }
      );
    } catch (error) {
      console.error('❌ ADMIN NOTIFICATION FAILED', error);
    }
  }

  private async answerCallbackQuery(bookingId: string, text: string, showAlert: boolean = false): Promise<void> {
    const botToken = this.getBotToken();
    if (!botToken) {
      console.error('❌ BOT TOKEN IS MISSING');
      return;
    }

    await axios.post(
      `https://api.telegram.org/bot${botToken}/answerCallbackQuery`,
      {
        callback_query_id: bookingId,
        text,
        show_alert: showAlert
      }
    );
  }

  private async editMessageText(chatId: string, messageId: number, text: string): Promise<void> {
    const botToken = this.getBotToken();
    if (!botToken) {
      console.error('❌ BOT TOKEN IS MISSING');
      return;
    }

    await axios.post(
      `https://api.telegram.org/bot${botToken}/editMessageText`,
      {
        chat_id: chatId,
        message_id: messageId,
        text,
        parse_mode: 'HTML'
      }
    );
  }

  // Методы для получения токена и chat ID с дополнительной проверкой
  private getBotToken(): string {
    return (
      import.meta.env.VITE_TELEGRAM_BOT_TOKEN || 
      process.env.VITE_TELEGRAM_BOT_TOKEN || 
      process.env.TELEGRAM_BOT_TOKEN || 
      ''
    );
  }

  private getAdminChatId(): string {
    return (
      import.meta.env.VITE_TELEGRAM_ADMIN_CHAT_ID || 
      process.env.VITE_TELEGRAM_ADMIN_CHAT_ID || 
      process.env.TELEGRAM_ADMIN_CHAT_ID || 
      ''
    );
  }

  // Остальной код остается без изменений
}

// Экспорт синглтона
export const telegramNotificationService = TelegramNotificationService.getInstance();

// Функция с повторными попытками
export async function sendBookingToTelegramWithRetry(
  booking: BookingData, 
  maxRetries: number = 3
): Promise<boolean> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await telegramNotificationService.sendBookingNotification(booking);
      
      if (result) {
        return true;
      }

      // Если отправка не удалась, ждем перед следующей попыткой
      await new Promise(resolve => setTimeout(resolve, attempt * 1000));
    } catch {
      // Если произошла ошибка, продолжаем попытки
      if (attempt === maxRetries) {
        return false;
      }
    }
  }

  return false;
}

export async function sendBookingToTelegram(booking: BookingData): Promise<{success: boolean, result?: any}> {
  const result = await telegramNotificationService.sendBookingNotification(booking);
  return { success: result };
}