/**
 * Enhanced Kanban Board
 * Улучшенная Kanban доска с drag & drop и real-time обновлениями
 */

import React, { useState, useEffect } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  DragOverlay,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { useBookingStore, useUIStore } from '../../../stores';
import { useBookingEvents } from '../../../hooks/useWebSocket';
import { BookingState, EnhancedBooking } from '../../../stores/types';
import { KanbanColumn } from './KanbanColumn';
import { KanbanCard } from './KanbanCard';
import LoadingSpinner from '../../common/LoadingSpinner';
import { PlusIcon } from '@heroicons/react/24/outline';

interface KanbanBoardProps {
  onCreateBooking?: () => void;
  onEditBooking?: (booking: EnhancedBooking) => void;
}

const COLUMN_CONFIG = [
  {
    id: BookingState.PENDING,
    title: 'Ожидает подтверждения',
    color: 'yellow',
    maxItems: 20,
  },
  {
    id: BookingState.CONFIRMED,
    title: 'Подтверждено',
    color: 'blue',
    maxItems: 15,
  },
  {
    id: BookingState.IN_PROGRESS,
    title: 'В процессе',
    color: 'indigo',
    maxItems: 10,
  },
  {
    id: BookingState.COMPLETED,
    title: 'Завершено',
    color: 'green',
    maxItems: 50,
  },
];

export const EnhancedKanbanBoard: React.FC<KanbanBoardProps> = ({
  onCreateBooking,
  onEditBooking,
}) => {
  const [activeBooking, setActiveBooking] = useState<EnhancedBooking | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const {
    bookings,
    fetchBookings,
    transitionBookingState,
    loading,
    error,
  } = useBookingStore();

  const { showSuccess, showError } = useUIStore();

  // Setup sensors for drag and drop
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Setup real-time event handlers
  useBookingEvents({
    onBookingCreated: () => {
      showSuccess('Новое бронирование добавлено на доску');
      fetchBookings();
    },
    onBookingUpdated: () => {
      fetchBookings();
    },
    onBookingStateChanged: (event) => {
      showSuccess(`Статус бронирования изменен: ${event.to_state}`);
      fetchBookings();
    },
    onBookingCancelled: () => {
      fetchBookings();
    },
  });

  // Load bookings on mount
  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  // Group bookings by state
  const groupedBookings = bookings.reduce((acc, booking) => {
    if (!acc[booking.state]) {
      acc[booking.state] = [];
    }
    acc[booking.state].push(booking);
    return acc;
  }, {} as Record<BookingState, EnhancedBooking[]>);

  // Sort bookings within each column by priority and date
  Object.keys(groupedBookings).forEach(state => {
    groupedBookings[state as BookingState].sort((a, b) => {
      // First sort by priority
      const priorityOrder = { urgent: 4, high: 3, normal: 2, low: 1 };
      const aPriority = priorityOrder[a.priority] || 2;
      const bPriority = priorityOrder[b.priority] || 2;
      
      if (aPriority !== bPriority) {
        return bPriority - aPriority;
      }
      
      // Then by booking date
      return new Date(a.booking_date).getTime() - new Date(b.booking_date).getTime();
    });
  });

  const handleDragStart = (event: DragStartEvent) => {
    const booking = bookings.find(b => b.id.toString() === event.active.id);
    setActiveBooking(booking || null);
    setIsDragging(true);
  };

  const handleDragOver = (event: DragOverEvent) => {
    // Optional: Handle drag over logic if needed
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setIsDragging(false);
    setActiveBooking(null);

    if (!over) return;

    const bookingId = parseInt(active.id as string);
    const newState = over.id as BookingState;
    
    const booking = bookings.find(b => b.id === bookingId);
    if (!booking || booking.state === newState) return;

    // Validate state transition
    if (!isValidStateTransition(booking.state, newState)) {
      showError('Недопустимый переход статуса');
      return;
    }

    try {
      await transitionBookingState(bookingId, {
        new_state: newState,
        notes: `Перемещено через Kanban доску`,
      });
      
      showSuccess(`Бронирование перемещено в "${getColumnTitle(newState)}"`);
    } catch (error: any) {
      showError(error.message || 'Ошибка при изменении статуса');
    }
  };

  const isValidStateTransition = (from: BookingState, to: BookingState): boolean => {
    const validTransitions: Record<BookingState, BookingState[]> = {
      [BookingState.DRAFT]: [BookingState.PENDING, BookingState.CANCELLED],
      [BookingState.PENDING]: [BookingState.CONFIRMED, BookingState.CANCELLED],
      [BookingState.CONFIRMED]: [BookingState.IN_PROGRESS, BookingState.CANCELLED],
      [BookingState.IN_PROGRESS]: [BookingState.COMPLETED, BookingState.CANCELLED],
      [BookingState.COMPLETED]: [], // No transitions from completed
      [BookingState.CANCELLED]: [], // No transitions from cancelled
      [BookingState.NO_SHOW]: [], // No transitions from no-show
    };

    return validTransitions[from]?.includes(to) || false;
  };

  const getColumnTitle = (state: BookingState): string => {
    return COLUMN_CONFIG.find(col => col.id === state)?.title || state;
  };

  const getColumnStats = (state: BookingState) => {
    const bookingsInColumn = groupedBookings[state] || [];
    const config = COLUMN_CONFIG.find(col => col.id === state);
    
    return {
      count: bookingsInColumn.length,
      maxItems: config?.maxItems || 0,
      totalValue: bookingsInColumn.reduce((sum, booking) => sum + booking.total_price, 0),
    };
  };

  if (loading && bookings.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner className="w-8 h-8" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">
          Загрузка Kanban доски...
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
              Ошибка загрузки Kanban доски
            </h3>
            <div className="mt-2 text-sm text-red-700 dark:text-red-300">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Kanban доска
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Управление бронированиями с помощью drag & drop
          </p>
        </div>

        {onCreateBooking && (
          <button
            onClick={onCreateBooking}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Новое бронирование
          </button>
        )}
      </div>

      {/* Kanban Board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 h-full">
          {COLUMN_CONFIG.map((column) => {
            const columnBookings = groupedBookings[column.id] || [];
            const stats = getColumnStats(column.id);
            
            return (
              <SortableContext
                key={column.id}
                items={columnBookings.map(b => b.id.toString())}
                strategy={verticalListSortingStrategy}
              >
                <KanbanColumn
                  id={column.id}
                  title={column.title}
                  color={column.color}
                  count={stats.count}
                  maxItems={stats.maxItems}
                  totalValue={stats.totalValue}
                  isDragOver={isDragging}
                >
                  {columnBookings.map((booking) => (
                    <KanbanCard
                      key={booking.id}
                      booking={booking}
                      onEdit={onEditBooking}
                      isDragging={activeBooking?.id === booking.id}
                    />
                  ))}
                </KanbanColumn>
              </SortableContext>
            );
          })}
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeBooking ? (
            <KanbanCard
              booking={activeBooking}
              onEdit={onEditBooking}
              isDragging={true}
              isOverlay={true}
            />
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Summary */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {bookings.length}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Всего бронирований
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {(groupedBookings[BookingState.PENDING] || []).length}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Ожидает подтверждения
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {(groupedBookings[BookingState.CONFIRMED] || []).length}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Подтверждено
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {(groupedBookings[BookingState.COMPLETED] || []).length}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Завершено
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedKanbanBoard;
