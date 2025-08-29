import { Telegraf } from 'telegraf';
import { TELEGRAM_CONFIG } from './services/telegram/config';

const bot = new Telegraf(TELEGRAM_CONFIG.botToken || '');

bot.start((ctx) => {
  ctx.reply('Добро пожаловать! Я бот для управления бронированиями.');
});

bot.on('text', (ctx) => {
  const message = ctx.message.text;
  ctx.reply(`You said: ${message}`);
});

bot.launch().then(() => {
  console.log('Telegram bot запущен');
}).catch((error) => {
  console.error('Ошибка запуска Telegram бота:', error);
});

// Graceful shutdown
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
