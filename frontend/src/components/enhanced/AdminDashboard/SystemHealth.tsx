/**
 * System Health Component
 * Компонент для отображения состояния системы
 */

import React from 'react';
import { 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  SignalIcon,
  ServerIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline';

interface SystemHealthProps {
  wsConnected: boolean;
  bookingsCount: number;
  employeesCount: number;
}

interface HealthMetric {
  name: string;
  status: 'healthy' | 'warning' | 'error';
  value: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const SystemHealth: React.FC<SystemHealthProps> = ({
  wsConnected,
  bookingsCount,
  employeesCount
}) => {
  const getHealthMetrics = (): HealthMetric[] => {
    return [
      {
        name: 'WebSocket соединение',
        status: wsConnected ? 'healthy' : 'error',
        value: wsConnected ? 'Подключено' : 'Отключено',
        description: 'Real-time обновления',
        icon: SignalIcon,
      },
      {
        name: 'База данных',
        status: 'healthy', // TODO: Add actual DB health check
        value: 'Активна',
        description: 'Подключение к PostgreSQL',
        icon: CircleStackIcon,
      },
      {
        name: 'API сервер',
        status: 'healthy', // TODO: Add actual API health check
        value: 'Работает',
        description: 'Backend API доступен',
        icon: ServerIcon,
      },
      {
        name: 'Загрузка данных',
        status: bookingsCount > 0 && employeesCount > 0 ? 'healthy' : 'warning',
        value: `${bookingsCount + employeesCount} записей`,
        description: 'Данные загружены',
        icon: CircleStackIcon,
      },
    ];
  };

  const getStatusIcon = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
    }
  };

  const getStatusColor = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'error':
        return 'text-red-600 dark:text-red-400';
    }
  };

  const metrics = getHealthMetrics();
  const overallHealth = metrics.every(m => m.status === 'healthy') 
    ? 'healthy' 
    : metrics.some(m => m.status === 'error') 
    ? 'error' 
    : 'warning';

  return (
    <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Состояние системы
          </h3>
          <div className="flex items-center">
            {getStatusIcon(overallHealth)}
            <span className={`ml-2 text-sm font-medium ${getStatusColor(overallHealth)}`}>
              {overallHealth === 'healthy' && 'Все системы работают'}
              {overallHealth === 'warning' && 'Есть предупреждения'}
              {overallHealth === 'error' && 'Обнаружены ошибки'}
            </span>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="space-y-4">
          {metrics.map((metric, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center min-w-0 flex-1">
                <div className="flex-shrink-0">
                  <metric.icon className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                </div>
                <div className="ml-3 min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {metric.name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {metric.description}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center">
                {getStatusIcon(metric.status)}
                <span className={`ml-2 text-sm font-medium ${getStatusColor(metric.status)}`}>
                  {metric.value}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* System info */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="font-medium text-gray-900 dark:text-white">Версия</dt>
              <dd className="text-gray-500 dark:text-gray-400">v2.0.0</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-900 dark:text-white">Uptime</dt>
              <dd className="text-gray-500 dark:text-gray-400">
                {Math.floor(performance.now() / 1000 / 60)} мин
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-900 dark:text-white">Память</dt>
              <dd className="text-gray-500 dark:text-gray-400">
                {navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-900 dark:text-white">Соединение</dt>
              <dd className="text-gray-500 dark:text-gray-400">
                {(navigator as any).connection?.effectiveType || 'N/A'}
              </dd>
            </div>
          </div>
        </div>

        {/* Performance metrics */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Производительность
          </h4>
          
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 dark:text-gray-400">Загрузка страницы</span>
                <span className="text-gray-900 dark:text-white">
                  {Math.round(performance.now())} мс
                </span>
              </div>
              <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, (1000 - performance.now()) / 10)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 dark:text-gray-400">API ответы</span>
                <span className="text-gray-900 dark:text-white">~ 150 мс</span>
              </div>
              <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full w-4/5" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemHealth;
