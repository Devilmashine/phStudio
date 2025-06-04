type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: any;
}

class Logger {
  private static instance: Logger;
  private logEntries: LogEntry[] = [];

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private log(level: LogLevel, message: string, data?: any) {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      data
    };

    this.logEntries.push(entry);
    
    // В разработке выводим в консоль
    if (process.env.NODE_ENV === 'development') {
      const logMethod = console[level] || console.log;
      if (data) {
        logMethod(`[${level.toUpperCase()}] ${message}`, data);
      } else {
        logMethod(`[${level.toUpperCase()}] ${message}`);
      }
    }
  }

  debug(message: string, data?: any) {
    this.log('debug', message, data);
  }

  info(message: string, data?: any) {
    this.log('info', message, data);
  }

  warn(message: string, data?: any) {
    this.log('warn', message, data);
  }

  error(message: string, data?: any) {
    this.log('error', message, data);
  }

  getLogEntries(): LogEntry[] {
    return [...this.logEntries];
  }

  clearLogs() {
    this.logEntries = [];
  }
}

export const logger = Logger.getInstance(); 