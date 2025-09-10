/**
 * Enhanced Kanban Hook
 * Integrates with existing Zustand stores for comprehensive state management
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useBookingStore } from '../stores/bookingStore';
import { useUIStore } from '../stores/uiStore';
import kanbanService, { KanbanFilters, KanbanBoardData } from '../services/kanbanService.enhanced';
import { KanbanColumn, KanbanCard, MoveCardRequest } from '../types/kanban';
import { useWebSocket } from './useWebSocket';

interface UseEnhancedKanbanOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  enableRealtime?: boolean;
}

interface UseEnhancedKanbanReturn {
  // Data
  columns: KanbanColumn[];
  cards: Record<string, KanbanCard[]>;
  loading: boolean;
  error: string | null;
  
  // Search and filters
  searchQuery: string;
  filters: KanbanFilters;
  setSearchQuery: (query: string) => void;
  setFilters: (filters: KanbanFilters | ((prev: KanbanFilters) => KanbanFilters)) => void;
  clearFilters: () => void;
  
  // Actions
  refreshBoard: () => Promise<void>;
  moveCard: (cardId: number, moveRequest: MoveCardRequest) => Promise<boolean>;
  updateCard: (cardId: number, updates: Partial<KanbanCard>) => Promise<boolean>;
  deleteCard: (cardId: number) => Promise<boolean>;
  
  // Statistics
  boardStats: {
    totalCards: number;
    cardsByColumn: Record<string, number>;
    averageTimeInColumn: Record<string, number>;
    revenueByColumn: Record<string, number>;
  } | null;
  
  // Real-time status
  isConnected: boolean;
  connectionStatus: string;
}

export const useEnhancedKanban = (options: UseEnhancedKanbanOptions = {}): UseEnhancedKanbanReturn => {
  const {
    autoRefresh = true,
    refreshInterval = 30000, // 30 seconds
    enableRealtime = true,
  } = options;

  // Zustand stores
  const { currentEmployee, isAuthenticated, token } = useAuthStore();
  const { 
    bookings, 
    isLoading: bookingsLoading, 
    error: bookingsError,
    fetchBookings,
    updateBooking,
    deleteBooking,
  } = useBookingStore();
  const { setGlobalLoading, addNotification } = useUIStore();

  // Local state
  const [columns, setColumns] = useState<KanbanColumn[]>([]);
  const [cards, setCards] = useState<Record<string, KanbanCard[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<KanbanFilters>({});
  const [boardStats, setBoardStats] = useState<UseEnhancedKanbanReturn['boardStats']>(null);

  // WebSocket for real-time updates
  const wsUrl = useMemo(() => {
    if (!enableRealtime || !token) return null;
    return `ws://localhost:8000/api/v2/ws/kanban?token=${token}`;
  }, [enableRealtime, token]);
  
  const { 
    lastMessage, 
    connectionStatus, 
    isConnected 
  } = useWebSocket(wsUrl);

  // Fetch board data
  const fetchBoardData = useCallback(async (searchFilters?: KanbanFilters) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await kanbanService.getBoardData(searchFilters || filters);
      
      setColumns(data.columns || []);
      setCards(data.cards || {});
      
      // Also update the booking store with fresh data
      await fetchBookings();
      
    } catch (err: any) {
      console.error('Error fetching kanban board:', err);
      
      // Fallback to existing booking data if available
      if (bookings.length > 0) {
        // Transform bookings to kanban format
        const kanbanCards = bookings.map(booking => ({
          id: booking.id,
          reference: booking.reference || `REF-${booking.id}`,
          title: `${booking.service || 'Studio Session'} - ${booking.duration}h`,
          client_name: booking.clientName,
          start_time: booking.startTime,
          end_time: booking.endTime,
          state: booking.status,
          column_id: booking.status,
        }));
        
        // Organize by status
        const organizedCards: Record<string, KanbanCard[]> = {
          new: [],
          confirmed: [],
          in_progress: [],
          completed: [],
          cancelled: [],
        };
        
        kanbanCards.forEach(card => {
          if (organizedCards[card.column_id]) {
            organizedCards[card.column_id].push(card);
          }
        });
        
        setCards(organizedCards);
        
        // Set default columns if not available
        if (columns.length === 0) {
          setColumns([
            { id: 'new', title: 'New Bookings', order: 1, color: '#3B82F6' },
            { id: 'confirmed', title: 'Confirmed', order: 2, color: '#10B981' },
            { id: 'in_progress', title: 'In Progress', order: 3, color: '#F59E0B' },
            { id: 'completed', title: 'Completed', order: 4, color: '#6B7280' },
            { id: 'cancelled', title: 'Cancelled', order: 5, color: '#EF4444' },
          ]);
        }
        
        setError('Using local booking data. API integration available.');
      } else {
        setError('Failed to load kanban board data');
      }
    } finally {
      setLoading(false);
    }
  }, [filters, bookings, fetchBookings, columns.length]);

  // Return hook interface
  return {
    // Data
    columns,
    cards,
    loading: loading || bookingsLoading,
    error: error || bookingsError,
    
    // Search and filters
    searchQuery,
    filters,
    setSearchQuery,
    setFilters,
    clearFilters: useCallback(() => {
      setFilters({});
      setSearchQuery('');
      fetchBoardData({});
    }, [fetchBoardData]),
    
    // Actions with optimistic updates
    refreshBoard: fetchBoardData,
    moveCard: useCallback(async (cardId: number, moveRequest: MoveCardRequest): Promise<boolean> => {
      try {
        // Optimistic update - move card immediately in UI
        const cardToMove = Object.values(cards).flat().find(card => card.id === cardId);
        if (cardToMove) {
          const newCards = { ...cards };
          
          // Remove card from current column
          Object.keys(newCards).forEach(columnId => {
            newCards[columnId] = newCards[columnId].filter(card => card.id !== cardId);
          });
          
          // Add card to new column with optimistic state
          const optimisticCard = { ...cardToMove, column_id: moveRequest.newColumnId, state: moveRequest.newColumnId };
          if (!newCards[moveRequest.newColumnId]) {
            newCards[moveRequest.newColumnId] = [];
          }
          newCards[moveRequest.newColumnId].push(optimisticCard);
          
          setCards(newCards);
          
          addNotification({
            type: 'info',
            message: `Moving ${cardToMove.title || cardToMove.reference} to ${moveRequest.newColumnId}...`,
            duration: 3000
          });
        }
        
        // Make API call
        const updatedCard = await kanbanService.moveCard(cardId, moveRequest);
        
        // Update booking store if needed
        if (updatedCard) {
          await updateBooking(cardId, { status: moveRequest.newColumnId });
          
          addNotification({
            type: 'success',
            message: `Card moved successfully!`,
            duration: 3000
          });
        }
        
        // Refresh to ensure consistency
        await fetchBoardData();
        
        return true;
      } catch (err: any) {
        console.error('Failed to move card:', err);
        
        // Revert optimistic update on failure
        await fetchBoardData();
        
        addNotification({
          type: 'error',
          message: `Failed to move card: ${err.message || 'Unknown error'}`,
          duration: 5000
        });
        
        return false;
      }
    }, [cards, kanbanService, addNotification, updateBooking, fetchBoardData]),
    
    updateCard: useCallback(async (cardId: number, updates: Partial<KanbanCard>): Promise<boolean> => {
      try {
        // Optimistic update - update card immediately in UI
        const newCards = { ...cards };
        let cardFound = false;
        
        Object.keys(newCards).forEach(columnId => {
          const cardIndex = newCards[columnId].findIndex(card => card.id === cardId);
          if (cardIndex !== -1) {
            newCards[columnId][cardIndex] = { ...newCards[columnId][cardIndex], ...updates };
            cardFound = true;
          }
        });
        
        if (cardFound) {
          setCards(newCards);
          addNotification({
            type: 'info',
            message: 'Updating card...',
            duration: 2000
          });
        }
        
        // Make API call
        const updatedCard = await kanbanService.updateCard(cardId, updates);
        
        if (updatedCard) {
          addNotification({
            type: 'success',
            message: 'Card updated successfully!',
            duration: 3000
          });
        }
        
        // Refresh to ensure consistency
        await fetchBoardData();
        
        return true;
      } catch (err: any) {
        console.error('Failed to update card:', err);
        
        // Revert optimistic update on failure
        await fetchBoardData();
        
        addNotification({
          type: 'error',
          message: `Failed to update card: ${err.message || 'Unknown error'}`,
          duration: 5000
        });
        
        return false;
      }
    }, [cards, kanbanService, addNotification, fetchBoardData]),
    
    deleteCard: useCallback(async (cardId: number): Promise<boolean> => {
      try {
        // Optimistic update - remove card immediately from UI
        const newCards = { ...cards };
        let deletedCard: KanbanCard | null = null;
        
        Object.keys(newCards).forEach(columnId => {
          const cardIndex = newCards[columnId].findIndex(card => card.id === cardId);
          if (cardIndex !== -1) {
            deletedCard = newCards[columnId][cardIndex];
            newCards[columnId].splice(cardIndex, 1);
          }
        });
        
        if (deletedCard) {
          setCards(newCards);
          addNotification({
            type: 'info',
            message: `Deleting ${deletedCard.title || deletedCard.reference}...`,
            duration: 3000
          });
        }
        
        // Make API call
        await kanbanService.deleteCard(cardId);
        
        // Update booking store
        await deleteBooking(cardId);
        
        addNotification({
          type: 'success',
          message: 'Card deleted successfully!',
          duration: 3000
        });
        
        return true;
      } catch (err: any) {
        console.error('Failed to delete card:', err);
        
        // Revert optimistic update on failure
        await fetchBoardData();
        
        addNotification({
          type: 'error',
          message: `Failed to delete card: ${err.message || 'Unknown error'}`,
          duration: 5000
        });
        
        return false;
      }
    }, [cards, kanbanService, addNotification, deleteBooking, fetchBoardData])
    
    // Statistics
    boardStats,
    
    // Real-time status
    isConnected,
    connectionStatus,
  };
};
