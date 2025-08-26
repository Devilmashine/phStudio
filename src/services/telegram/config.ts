import dotenv from 'dotenv';
import path from 'path';

// Explicitly log all environment variables related to Telegram
console.warn('🚨 ENVIRONMENT VARIABLES DUMP 🚨');
console.log('🌍 Full Environment Variables:', Object.keys(process.env)
  .filter(key => 
    key.includes('TELEGRAM') || 
    key.includes('VITE_TELEGRAM')
  )
  .reduce((acc, key) => {
    acc[key] = process.env[key] ? '✅ PRESENT (masked)' : '❌ MISSING';
    return acc;
  }, {} as Record<string, string>)
);

// Принудительная загрузка .env файла с полным путем
const envPath = path.resolve(process.cwd(), '.env');
console.warn('🚨 LOADING ENV FILE FROM: 🚨', envPath);

dotenv.config({ path: envPath });

// Принудительная загрузка переменных из process.env
console.warn('🚨 ENVIRONMENT VARIABLES INITIALIZATION 🚨');

// Логирование всех переменных окружения
console.log('🌍 ALL Environment Variables:', 
  Object.keys(process.env)
    .filter(key => 
      key.includes('TELEGRAM') || 
      key.includes('VITE_TELEGRAM')
    )
    .reduce((acc, key) => {
      acc[key] = process.env[key] ? '✅ PRESENT (masked)' : '❌ MISSING';
      return acc;
    }, {} as Record<string, string>)
);

// Additional runtime environment check
console.warn('🚨 RUNTIME ENVIRONMENT CHECK 🚨');
console.log('🌐 Runtime Environment:', {
  nodeEnv: process.env.NODE_ENV,
  viteMode: import.meta.env?.MODE,
  viteEnv: import.meta.env
});

// Расширенная диагностика загрузки
console.warn('🚨 RUNTIME ENVIRONMENT DEEP CHECK 🚨');
console.log('🌐 Detailed Runtime Environment:', {
  nodeEnv: process.env.NODE_ENV,
  viteMode: (import.meta.env as any)?.MODE,
  viteEnv: import.meta.env,
  
  // Специфические переменные Telegram
  botTokenSource: process.env.TELEGRAM_BOT_TOKEN 
    ? 'TELEGRAM_BOT_TOKEN' 
    : process.env.VITE_TELEGRAM_BOT_TOKEN 
      ? 'VITE_TELEGRAM_BOT_TOKEN' 
      : '❌ NOT FOUND',
  
  adminChatIdSource: process.env.TELEGRAM_ADMIN_CHAT_ID 
    ? 'TELEGRAM_ADMIN_CHAT_ID' 
    : process.env.VITE_TELEGRAM_ADMIN_CHAT_ID 
      ? 'VITE_TELEGRAM_ADMIN_CHAT_ID' 
      : '❌ NOT FOUND'
});

// Конфигурация Telegram
export const TELEGRAM_CONFIG = {
  botToken: process.env.VITE_TELEGRAM_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN || '',
  adminChatId: process.env.VITE_TELEGRAM_ADMIN_CHAT_ID || process.env.TELEGRAM_ADMIN_CHAT_ID || '',
  webhookUrl: process.env.VITE_TELEGRAM_WEBHOOK_URL || process.env.TELEGRAM_WEBHOOK_URL || ''
};

// Проверка конфигурации
if (!TELEGRAM_CONFIG.botToken) {
  console.error('❌ CRITICAL: Telegram Bot Token is MISSING');
  console.error('🔍 Available Telegram-related environment variables:', 
    Object.keys(process.env).filter(key => 
      key.includes('TELEGRAM') || key.includes('VITE_TELEGRAM')
    )
  );
}

// Диагностическое логирование
console.warn('🚨 TELEGRAM CONFIG INITIALIZATION 🚨', {
  botTokenPresent: !!TELEGRAM_CONFIG.botToken,
  adminChatIdPresent: !!TELEGRAM_CONFIG.adminChatId,
  webhookUrlPresent: !!TELEGRAM_CONFIG.webhookUrl
});

// Log configuration for debugging with actual values
console.warn('🚨 FORCED TELEGRAM CONFIG LOGGING 🚨');
console.log('🤖 Telegram Configuration (DETAILED):', {
  botToken: TELEGRAM_CONFIG.botToken ? '✅ PRESENT (masked)' : '❌ MISSING',
  adminChatId: TELEGRAM_CONFIG.adminChatId ? '✅ PRESENT' : '❌ MISSING',
  webhookUrl: TELEGRAM_CONFIG.webhookUrl ? '✅ PRESENT' : '❌ MISSING',
  
  // Environment variables for cross-checking
  envBotToken: process.env.TELEGRAM_BOT_TOKEN ? '✅ PRESENT' : '❌ MISSING',
  envViteBotToken: process.env.VITE_TELEGRAM_BOT_TOKEN ? '✅ PRESENT' : '❌ MISSING',
  
  envAdminChatId: process.env.TELEGRAM_ADMIN_CHAT_ID ? '✅ PRESENT' : '❌ MISSING',
  envViteAdminChatId: process.env.VITE_TELEGRAM_ADMIN_CHAT_ID ? '✅ PRESENT' : '❌ MISSING',
  
  envWebhookUrl: process.env.TELEGRAM_WEBHOOK_URL ? '✅ PRESENT' : '❌ MISSING',
  envViteWebhookUrl: process.env.VITE_TELEGRAM_WEBHOOK_URL ? '✅ PRESENT' : '❌ MISSING'
});

// Финальная проверка конфигурации
console.warn('🚨 FINAL TELEGRAM CONFIG VALIDATION 🚨');
console.log('🤖 Telegram Configuration:', {
  botToken: TELEGRAM_CONFIG.botToken ? '✅ PRESENT (masked)' : '❌ MISSING',
  adminChatId: TELEGRAM_CONFIG.adminChatId ? '✅ PRESENT' : '❌ MISSING',
  
  // Детальная проверка источников
  botTokenSources: {
    processEnv: !!process.env.TELEGRAM_BOT_TOKEN,
    viteEnv: !!process.env.VITE_TELEGRAM_BOT_TOKEN
  },
  adminChatIdSources: {
    processEnv: !!process.env.TELEGRAM_ADMIN_CHAT_ID,
    viteEnv: !!process.env.VITE_TELEGRAM_ADMIN_CHAT_ID
  }
});

// Validate Telegram configuration
if (!TELEGRAM_CONFIG.botToken) {
  console.error('❌ CRITICAL: Telegram Bot Token is MISSING');
  console.error('🔍 Available Telegram-related environment variables:', 
    Object.keys(process.env).filter(key => 
      key.includes('TELEGRAM') || key.includes('VITE_TELEGRAM')
    )
  );
}

if (!TELEGRAM_CONFIG.adminChatId) {
  console.error('❌ CRITICAL: Telegram Admin Chat ID is MISSING');
}

// Строгая валидация конфигурации
if (!TELEGRAM_CONFIG.botToken) {
  throw new Error('Telegram Bot Token is not configured');
}

if (!TELEGRAM_CONFIG.adminChatId) {
  throw new Error('Telegram Admin Chat ID is not configured');
}