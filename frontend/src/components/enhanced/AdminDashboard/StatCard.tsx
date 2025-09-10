/**
 * Stat Card Component
 * Карточка для отображения статистики
 */

import React from 'react';
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  MinusIcon 
} from '@heroicons/react/24/solid';

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ComponentType<{ className?: string }>;
  color?: 'blue' | 'green' | 'indigo' | 'purple' | 'red' | 'yellow';
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-500',
    text: 'text-blue-600 dark:text-blue-400',
    lightBg: 'bg-blue-50 dark:bg-blue-900/20'
  },
  green: {
    bg: 'bg-green-500',
    text: 'text-green-600 dark:text-green-400',
    lightBg: 'bg-green-50 dark:bg-green-900/20'
  },
  indigo: {
    bg: 'bg-indigo-500',
    text: 'text-indigo-600 dark:text-indigo-400',
    lightBg: 'bg-indigo-50 dark:bg-indigo-900/20'
  },
  purple: {
    bg: 'bg-purple-500',
    text: 'text-purple-600 dark:text-purple-400',
    lightBg: 'bg-purple-50 dark:bg-purple-900/20'
  },
  red: {
    bg: 'bg-red-500',
    text: 'text-red-600 dark:text-red-400',
    lightBg: 'bg-red-50 dark:bg-red-900/20'
  },
  yellow: {
    bg: 'bg-yellow-500',
    text: 'text-yellow-600 dark:text-yellow-400',
    lightBg: 'bg-yellow-50 dark:bg-yellow-900/20'
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  color = 'blue'
}) => {
  const colors = colorClasses[color];

  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive':
        return <ArrowUpIcon className="w-4 h-4 text-green-500" />;
      case 'negative':
        return <ArrowDownIcon className="w-4 h-4 text-red-500" />;
      default:
        return <MinusIcon className="w-4 h-4 text-gray-400" />;
    }
  };

  const getChangeTextColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-green-600 dark:text-green-400';
      case 'negative':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow-sm rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`p-3 rounded-lg ${colors.lightBg}`}>
              <Icon className={`w-6 h-6 ${colors.text}`} />
            </div>
          </div>
          
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {value}
                </div>
                {change && (
                  <div className={`ml-2 flex items-baseline text-sm font-semibold ${getChangeTextColor()}`}>
                    {getChangeIcon()}
                    <span className="ml-1">{change}</span>
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatCard;
