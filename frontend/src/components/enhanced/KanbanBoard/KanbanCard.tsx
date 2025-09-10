/**
 * Kanban Card Component
 * Компонент карточки для Kanban доски
 */

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  UserIcon,
  PhoneIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  PencilIcon,
} from '@heroicons/react/24/outline';
import { EnhancedBooking, BookingPriority, SpaceType } from '../../../stores/types';

interface KanbanCardProps {
  booking: EnhancedBooking;
  onEdit?: (booking: EnhancedBooking) => void;
  isDragging?: boolean;
  isOverlay?: boolean;
}

const priorityColors = {
  [BookingPriority.LOW]: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  [BookingPriority.NORMAL]: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  [BookingPriority.HIGH]: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  [BookingPriority.URGENT]: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
};

const priorityLabels = {
  [BookingPriority.LOW]: 'Низкий',
  [BookingPriority.NORMAL]: 'Обычный',
  [BookingPriority.HIGH]: 'Высокий',
  [BookingPriority.URGENT]: 'Срочный',
};

const spaceTypeLabels = {
  [SpaceType.MAIN_STUDIO]: 'Основная студия',
  [SpaceType.SMALL_STUDIO]: 'Малая студия',
  [SpaceType.OUTDOOR_AREA]: 'Открытая площадка',
};

export const KanbanCard: React.FC<KanbanCardProps> = ({
  booking,
  onEdit,
  isDragging = false,
  isOverlay = false,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({
    id: booking.id.toString(),
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging || isSortableDragging ? 0.5 : 1,
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit'
    });
  };

  const isUrgent = booking.priority === BookingPriority.URGENT;
  const isHighPriority = booking.priority === BookingPriority.HIGH;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`
        bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 cursor-grab active:cursor-grabbing
        hover:shadow-md transition-all duration-200
        ${isOverlay ? 'shadow-lg rotate-3' : ''}
        ${isUrgent ? 'ring-2 ring-red-500 ring-opacity-50' : ''}
        ${isHighPriority && !isUrgent ? 'ring-1 ring-yellow-500 ring-opacity-50' : ''}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center min-w-0 flex-1">
          <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
            <UserIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          </div>
          <div className="ml-2 min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {booking.client_name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              #{booking.booking_reference}
            </p>
          </div>
        </div>

        {/* Priority badge */}
        {booking.priority !== BookingPriority.NORMAL && (
          <span className={`
            inline-flex items-center px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ml-2
            ${priorityColors[booking.priority]}
          `}>
            {isUrgent && <ExclamationTriangleIcon className="w-3 h-3 mr-1" />}
            {priorityLabels[booking.priority]}
          </span>
        )}
      </div>

      {/* Contact info */}
      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
        <PhoneIcon className="w-3 h-3 mr-1 flex-shrink-0" />
        <span className="truncate">{booking.client_phone}</span>
      </div>

      {/* Date and time */}
      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
        <ClockIcon className="w-3 h-3 mr-1 flex-shrink-0" />
        <span>
          {formatDate(booking.booking_date)} в {formatTime(booking.start_time)}
        </span>
      </div>

      {/* Space type */}
      <div className="text-xs text-gray-600 dark:text-gray-300 mb-3">
        📍 {spaceTypeLabels[booking.space_type]}
      </div>

      {/* Special requirements */}
      {booking.special_requirements && (
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-3 p-2 bg-gray-50 dark:bg-gray-700 rounded">
          <p className="line-clamp-2">
            💡 {booking.special_requirements}
          </p>
        </div>
      )}

      {/* Equipment */}
      {booking.equipment_requested && booking.equipment_requested.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {booking.equipment_requested.slice(0, 2).map((equipment, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded text-xs bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300"
              >
                🎬 {equipment.replace(/_/g, ' ')}
              </span>
            ))}
            {booking.equipment_requested.length > 2 && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                +{booking.equipment_requested.length - 2} еще
              </span>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center text-sm font-medium text-gray-900 dark:text-white">
          <CurrencyDollarIcon className="w-4 h-4 mr-1 text-green-500" />
          {booking.total_price.toLocaleString('ru-RU')} ₽
        </div>

        {onEdit && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(booking);
            }}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
            title="Редактировать"
          >
            <PencilIcon className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Duration indicator */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
        ⏱️ {booking.duration_hours}ч ({formatTime(booking.start_time)} - {formatTime(booking.end_time)})
      </div>

      {/* State history indicator */}
      {booking.state_history && booking.state_history.length > 1 && (
        <div className="mt-2 text-xs text-gray-400 dark:text-gray-500">
          📝 {booking.state_history.length} изменений статуса
        </div>
      )}
    </div>
  );
};

export default KanbanCard;
