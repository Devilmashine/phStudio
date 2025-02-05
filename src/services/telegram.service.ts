import axios from 'axios';

interface BookingNotificationData {
  name: string;
  phone: string;
  date: string;
  times: string[];
  totalPrice: number;
  comment?: string;
}

class TelegramService {
  private apiUrl = '/api/telegram/notify';

  async sendBookingNotification(bookingData: BookingNotificationData) {
    try {
      const response = await axios.post(this.apiUrl, bookingData);
      
      if (response.data && response.data.status === 'success') {
        console.log('Уведомление в Telegram отправлено');
        return true;
      }
      
      throw new Error('Не удалось отправить уведомление в Telegram');
    } catch (error) {
      console.error('Ошибка отправки уведомления в Telegram:', error);
      throw error;
    }
  }
}

export const telegramService = new TelegramService();
