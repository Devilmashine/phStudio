import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { useWebSocket } from '../hooks/useWebSocket';
import authService from '../services/authService';
import kanbanService, { KanbanFilters } from '../services/kanbanService.enhanced';

interface KanbanColumn {
  id: string;
  title: string;
  order: number;
  color: string;
}

interface KanbanCard {
  id: number;
  reference: string;
  title: string;
  clientName: string;
  startTime: string;
  endTime: string;
  state: string;
  columnId: string;
}

const KanbanBoard: React.FC = () => {
  const [columns, setColumns] = useState<KanbanColumn[]>([]);
  const [cards, setCards] = useState<Record<string, KanbanCard[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<KanbanFilters>({});
  
  // Get token for WebSocket authentication
  const token = authService.getToken();
  const wsUrl = token 
    ? `ws://localhost:8000/api/v2/ws/kanban?token=${token}`
    : 'ws://localhost:8000/api/v2/ws/kanban';
  
  // WebSocket connection for real-time updates
  const ws = useWebSocket(token ? wsUrl : null);
  
  // Fetch board data with filters
  const fetchBoardData = async (searchFilters?: KanbanFilters) => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch from the enhanced API service
      const data = await kanbanService.getBoardData(searchFilters || filters);
      
      setColumns(data.columns || []);
      setCards(data.cards || {});
        setLoading(false);
      } catch (err) {
        console.error('Error fetching kanban board:', err);
        
        // Fallback to mock data for demo purposes
        const mockColumns: KanbanColumn[] = [
          { id: 'new', title: 'New Bookings', order: 1, color: '#3B82F6' },
          { id: 'confirmed', title: 'Confirmed', order: 2, color: '#10B981' },
          { id: 'in_progress', title: 'In Progress', order: 3, color: '#F59E0B' },
          { id: 'completed', title: 'Completed', order: 4, color: '#6B7280' },
          { id: 'cancelled', title: 'Cancelled', order: 5, color: '#EF4444' },
        ];
        
        const mockCards: Record<string, KanbanCard[]> = {
          new: [
            {
              id: 1,
              reference: 'REF-20240101-0001',
              title: 'Studio Session - 2h',
              clientName: 'John Doe',
              startTime: '2024-01-01T10:00:00',
              endTime: '2024-01-01T12:00:00',
              state: 'pending',
              columnId: 'new'
            }
          ],
          confirmed: [
            {
              id: 2,
              reference: 'REF-20240101-0002',
              title: 'Portrait Session - 1h',
              clientName: 'Jane Smith',
              startTime: '2024-01-01T14:00:00',
              endTime: '2024-01-01T15:00:00',
              state: 'confirmed',
              columnId: 'confirmed'
            }
          ],
          in_progress: [],
          completed: [],
          cancelled: []
        };
        
        setColumns(mockColumns);
        setCards(mockCards);
        setError('Connected to demo data. API integration available.');
        setLoading(false);
      }
    }
  };
  
  // Initial data fetch
  useEffect(() => {
    fetchBoardData();
  }, []);
  
  // Refetch data when filters change
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchBoardData();
    }, 500); // Debounce filter changes
    
    return () => clearTimeout(timeoutId);
  }, [filters]);
  
  // Search handler
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      fetchBoardData();
      return;
    }
    
    try {
      setLoading(true);
      const searchResults = await kanbanService.searchCards(query, filters);
      
      // Organize search results by column
      const organizedCards: Record<string, KanbanCard[]> = {};
      columns.forEach(column => {
        organizedCards[column.id] = [];
      });
      
      searchResults.forEach(card => {
        if (organizedCards[card.column_id]) {
          organizedCards[card.column_id].push(card);
        }
      });
      
      setCards(organizedCards);
      setLoading(false);
    } catch (err) {
      console.error('Search error:', err);
      setError('Search failed. Please try again.');
      setLoading(false);
    }
  };
  
  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(searchQuery);
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);
  
  // Handle WebSocket messages
  useEffect(() => {
    if (ws.lastMessage) {
      try {
        const message = JSON.parse(ws.lastMessage);
        if (message.type === 'card_moved') {
          // Update the UI based on the card move
          setCards(prevCards => {
            const newCards = { ...prevCards };
            // Find and move the card
            for (const columnId in newCards) {
              const columnCards = newCards[columnId];
              const cardIndex = columnCards.findIndex(card => card.id === message.card_id);
              if (cardIndex !== -1) {
                const [movedCard] = columnCards.splice(cardIndex, 1);
                movedCard.columnId = message.to_column_id;
                if (!newCards[message.to_column_id]) {
                  newCards[message.to_column_id] = [];
                }
                newCards[message.to_column_id].push(movedCard);
                break;
              }
            }
            return newCards;
          });
        }
      } catch (err) {
        console.error('Error processing WebSocket message:', err);
      }
    }
  }, [ws.lastMessage]);
  
  const onDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;
    
    // Dropped outside the list
    if (!destination) {
      return;
    }
    
    // Dropped in the same place
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }
    
    const cardId = parseInt(draggableId);
    
    // Store original state for rollback
    const originalCards = cards;
    
    // Update UI optimistically first
    setCards(prevCards => {
      const newCards = { ...prevCards };
      const sourceColumn = [...(newCards[source.droppableId] || [])];
      const [movedCard] = sourceColumn.splice(source.index, 1);
      
      movedCard.columnId = destination.droppableId;
      
      const destColumn = [...(newCards[destination.droppableId] || [])];
      destColumn.splice(destination.index, 0, movedCard);
      
      newCards[source.droppableId] = sourceColumn;
      newCards[destination.droppableId] = destColumn;
      
      return newCards;
    });
    
    try {
      // Make API call using enhanced service
      const currentEmployee = authService.getCurrentUser();
      
      await kanbanService.moveCard(cardId, {
        to_column_id: destination.droppableId,
        employee_id: currentEmployee?.id || 1
      });
      
      // API call successful - the optimistic update was correct
      console.log('Card moved successfully');
      
    } catch (err) {
      console.error('Error moving card:', err);
      
      // Rollback optimistic update
      setCards(originalCards);
      
      setError('Failed to move card. Please try again.');
      
      // Clear error after 3 seconds
      setTimeout(() => setError(null), 3000);
    }
  };
  
  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading Kanban Board...</div>;
  }
  
  if (error) {
    return <div className="text-red-500 text-center py-4">{error}</div>;
  }
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Booking Management Board</h1>
        
        {/* Search and Filter Controls */}
        <div className="flex gap-4 items-center">
          <div className="relative">
            <input
              type="text"
              placeholder="Search bookings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <svg className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <select
            value={filters.state || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, state: e.target.value || undefined }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All States</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          
          <select
            value={filters.spaceType || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, spaceType: e.target.value || undefined }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Spaces</option>
            <option value="studio_a">Studio A</option>
            <option value="studio_b">Studio B</option>
            <option value="studio_c">Studio C</option>
            <option value="outdoor">Outdoor</option>
          </select>
          
          <button
            onClick={() => {
              setFilters({});
              setSearchQuery('');
            }}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>
      
      {error && (
        <div className={`mb-4 p-3 rounded-lg ${error.includes('demo') ? 'bg-blue-50 text-blue-700' : 'bg-red-50 text-red-700'}`}>
          {error}
        </div>
      )}
      
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {columns.map(column => (
            <div key={column.id} className="bg-gray-50 rounded-lg shadow">
              <div 
                className="p-3 rounded-t-lg font-semibold text-white"
                style={{ backgroundColor: column.color }}
              >
                {column.title}
              </div>
              
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className={`p-2 min-h-[100px] ${snapshot.isDraggingOver ? 'bg-blue-50' : ''}`}
                  >
                    {cards[column.id]?.map((card, index) => (
                      <Draggable key={card.id.toString()} draggableId={card.id.toString()} index={index}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`bg-white p-3 mb-2 rounded shadow ${snapshot.isDragging ? 'shadow-lg' : ''}`}
                          >
                            <div className="font-semibold">{card.title}</div>
                            <div className="text-sm text-gray-600">{card.clientName}</div>
                            <div className="text-xs text-gray-500">
                              {new Date(card.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - 
                              {new Date(card.endTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <div className="text-xs text-gray-500">{card.reference}</div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};

export default KanbanBoard;