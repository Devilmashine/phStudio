/**
 * Kanban Column Component
 * Компонент колонки для Kanban доски
 */

import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { 
  ExclamationTriangleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline';

interface KanbanColumnProps {
  id: string;
  title: string;
  color: string;
  count: number;
  maxItems: number;
  totalValue: number;
  isDragOver: boolean;
  children: React.ReactNode;
}

const colorClasses = {
  yellow: {
    header: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
    title: 'text-yellow-800 dark:text-yellow-200',
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    accent: 'border-l-yellow-500',
  },
  blue: {
    header: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    title: 'text-blue-800 dark:text-blue-200',
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    accent: 'border-l-blue-500',
  },
  indigo: {
    header: 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800',
    title: 'text-indigo-800 dark:text-indigo-200',
    badge: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    accent: 'border-l-indigo-500',
  },
  green: {
    header: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    title: 'text-green-800 dark:text-green-200',
    badge: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    accent: 'border-l-green-500',
  },
  red: {
    header: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    title: 'text-red-800 dark:text-red-200',
    badge: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    accent: 'border-l-red-500',
  },
};

export const KanbanColumn: React.FC<KanbanColumnProps> = ({
  id,
  title,
  color,
  count,
  maxItems,
  totalValue,
  isDragOver,
  children,
}) => {
  const { setNodeRef, isOver } = useDroppable({
    id,
  });

  const colors = colorClasses[color as keyof typeof colorClasses] || colorClasses.blue;
  const isNearLimit = maxItems > 0 && count >= maxItems * 0.8;
  const isOverLimit = maxItems > 0 && count >= maxItems;

  return (
    <div
      ref={setNodeRef}
      className={`
        flex flex-col h-full bg-gray-50 dark:bg-gray-900 rounded-lg border-2 
        ${isOver ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-200 dark:border-gray-700'}
        ${colors.accent}
        transition-all duration-200
      `}
    >
      {/* Column Header */}
      <div className={`
        p-4 border-b border-gray-200 dark:border-gray-700 rounded-t-lg
        ${colors.header}
      `}>
        <div className="flex items-center justify-between mb-2">
          <h3 className={`font-semibold text-sm ${colors.title}`}>
            {title}
          </h3>
          
          <div className="flex items-center space-x-2">
            {isOverLimit && (
              <ExclamationTriangleIcon className="w-4 h-4 text-red-500" title="Превышен лимит" />
            )}
            {isNearLimit && !isOverLimit && (
              <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" title="Приближается к лимиту" />
            )}
            <span className={`
              inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
              ${colors.badge}
            `}>
              {count}
              {maxItems > 0 && ` / ${maxItems}`}
            </span>
          </div>
        </div>

        {/* Value indicator */}
        {totalValue > 0 && (
          <div className="text-xs text-gray-600 dark:text-gray-400">
            Сумма: {totalValue.toLocaleString('ru-RU')} ₽
          </div>
        )}

        {/* Progress bar for column capacity */}
        {maxItems > 0 && (
          <div className="mt-2">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
              <div 
                className={`
                  h-1 rounded-full transition-all duration-300
                  ${isOverLimit ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-green-500'}
                `}
                style={{ width: `${Math.min(100, (count / maxItems) * 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Column Content */}
      <div className="flex-1 p-3 overflow-y-auto">
        <div className="space-y-3">
          {children}
        </div>

        {/* Drop zone indicator */}
        {isOver && (
          <div className="mt-4 p-4 border-2 border-dashed border-indigo-300 dark:border-indigo-600 rounded-lg bg-indigo-50 dark:bg-indigo-900/20">
            <div className="text-center text-indigo-600 dark:text-indigo-400">
              <CheckCircleIcon className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm font-medium">Отпустите для перемещения</p>
            </div>
          </div>
        )}

        {/* Empty state */}
        {count === 0 && !isOver && (
          <div className="text-center py-8">
            <div className="text-gray-400 dark:text-gray-500">
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <span className="text-lg">📋</span>
              </div>
              <p className="text-sm">Нет бронирований</p>
            </div>
          </div>
        )}
      </div>

      {/* Column Footer */}
      {count > 0 && (
        <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-b-lg">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>
              {count} {count === 1 ? 'бронирование' : count < 5 ? 'бронирования' : 'бронирований'}
            </span>
            {totalValue > 0 && (
              <span className="font-medium">
                ср. {Math.round(totalValue / count).toLocaleString('ru-RU')} ₽
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default KanbanColumn;
