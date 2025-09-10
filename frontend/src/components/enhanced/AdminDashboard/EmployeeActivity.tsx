/**
 * Employee Activity Component
 * Компонент для отображения активности сотрудников
 */

import React from 'react';
import { 
  UserGroupIcon,
  UserIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { EnhancedEmployee, EmployeeStatus } from '../../../stores/types';
import LoadingSpinner from '../../common/LoadingSpinner';

interface EmployeeActivityProps {
  employees: EnhancedEmployee[];
  loading: boolean;
}

const statusColors = {
  [EmployeeStatus.PENDING_ACTIVATION]: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  [EmployeeStatus.ACTIVE]: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  [EmployeeStatus.INACTIVE]: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  [EmployeeStatus.SUSPENDED]: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  [EmployeeStatus.TERMINATED]: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
};

const statusLabels = {
  [EmployeeStatus.PENDING_ACTIVATION]: 'Ожидает активации',
  [EmployeeStatus.ACTIVE]: 'Активен',
  [EmployeeStatus.INACTIVE]: 'Неактивен',
  [EmployeeStatus.SUSPENDED]: 'Приостановлен',
  [EmployeeStatus.TERMINATED]: 'Уволен',
};

export const EmployeeActivity: React.FC<EmployeeActivityProps> = ({
  employees,
  loading
}) => {
  const getRecentActivity = () => {
    return employees
      .filter(emp => emp.last_activity)
      .sort((a, b) => 
        new Date(b.last_activity!).getTime() - new Date(a.last_activity!).getTime()
      )
      .slice(0, 5);
  };

  const getStatusStats = () => {
    const stats = employees.reduce((acc, emp) => {
      acc[emp.status] = (acc[emp.status] || 0) + 1;
      return acc;
    }, {} as Record<EmployeeStatus, number>);

    return Object.entries(stats).map(([status, count]) => ({
      status: status as EmployeeStatus,
      count,
      label: statusLabels[status as EmployeeStatus]
    }));
  };

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays < 7) return `${diffDays} дн назад`;
    
    return date.toLocaleDateString('ru-RU');
  };

  const recentActivity = getRecentActivity();
  const statusStats = getStatusStats();

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Активность сотрудников
          </h3>
        </div>
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner className="w-6 h-6 mr-2" />
          <span className="text-gray-600 dark:text-gray-400">Загрузка...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Активность сотрудников
          </h3>
          <UserGroupIcon className="w-5 h-5 text-gray-400" />
        </div>
      </div>

      <div className="p-6">
        {employees.length === 0 ? (
          <div className="text-center py-12">
            <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              Нет сотрудников
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Добавьте сотрудников для отслеживания их активности.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Status statistics */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Статус сотрудников
              </h4>
              <div className="grid grid-cols-1 gap-2">
                {statusStats.map(({ status, count, label }) => (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]}`}>
                        {label}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent activity */}
            {recentActivity.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  Последняя активность
                </h4>
                <div className="space-y-3">
                  {recentActivity.map((employee) => (
                    <div key={employee.id} className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
                          <UserIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </div>
                      </div>
                      
                      <div className="ml-3 min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {employee.full_name}
                        </p>
                        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                          <ClockIcon className="w-3 h-3 mr-1" />
                          {formatRelativeTime(employee.last_activity!)}
                        </div>
                      </div>
                      
                      <div className="flex-shrink-0">
                        {employee.status === EmployeeStatus.ACTIVE ? (
                          <CheckCircleIcon className="w-4 h-4 text-green-500" />
                        ) : (
                          <div className="w-4 h-4 rounded-full bg-gray-300 dark:bg-gray-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {employees.length}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Всего
                  </div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {employees.filter(e => e.status === EmployeeStatus.ACTIVE).length}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Активных
                  </div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-blue-600 dark:text-blue-400">
                    {recentActivity.length}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Онлайн
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeActivity;
