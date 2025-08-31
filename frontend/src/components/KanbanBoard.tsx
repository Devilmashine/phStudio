import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { useWebSocket } from '../hooks/useWebSocket';
import authService from '../services/authService';

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
  
  // Get token for WebSocket authentication
  const token = authService.getToken();
  const wsUrl = token 
    ? `ws://localhost:8000/api/v2/ws/kanban?token=${token}`
    : 'ws://localhost:8000/api/v2/ws/kanban';
  
  // WebSocket connection for real-time updates
  const ws = useWebSocket(token ? wsUrl : null);
  
  // Fetch initial board data
  useEffect(() => {
    const fetchBoardData = async () => {
      try {
        setLoading(true);
        // In a real implementation, we would fetch from our new API
        // const response = await fetch('/api/v2/kanban/board');
        // const data = await response.json();
        
        // Mock data for demonstration
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
              reference: 'REF-20230101-0001',
              title: 'Studio Session - 2h',
              clientName: 'John Doe',
              startTime: '2023-01-01T10:00:00',
              endTime: '2023-01-01T12:00:00',
              state: 'pending',
              columnId: 'new'
            }
          ],
          confirmed: [
            {
              id: 2,
              reference: 'REF-20230101-0002',
              title: 'Portrait Session - 1h',
              clientName: 'Jane Smith',
              startTime: '2023-01-01T14:00:00',
              endTime: '2023-01-01T15:00:00',
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
        setLoading(false);
      } catch (err) {
        setError('Failed to load kanban board data');
        setLoading(false);
      }
    };
    
    fetchBoardData();
  }, []);
  
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
    
    try {
      // In a real implementation, we would call our API
      // await fetch(`/api/v2/kanban/cards/${cardId}/move`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     to_column_id: destination.droppableId,
      //     employee_id: 1 // Get from auth context
      //   })
      // });
      
      // Update UI optimistically
      setCards(prevCards => {
        const newCards = { ...prevCards };
        const sourceColumn = [...newCards[source.droppableId]];
        const [movedCard] = sourceColumn.splice(source.index, 1);
        
        movedCard.columnId = destination.droppableId;
        
        const destColumn = [...newCards[destination.droppableId]];
        destColumn.splice(destination.index, 0, movedCard);
        
        newCards[source.droppableId] = sourceColumn;
        newCards[destination.droppableId] = destColumn;
        
        return newCards;
      });
    } catch (err) {
      setError('Failed to move card');
      // In a real implementation, we would rollback the optimistic update
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
      <h1 className="text-2xl font-bold mb-6">Booking Management Board</h1>
      
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