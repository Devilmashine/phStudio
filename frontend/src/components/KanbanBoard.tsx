import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import authService from '../services/authService';
import kanbanService, { KanbanFilters } from '../services/kanbanService.enhanced';
import { KanbanColumn, KanbanCard } from '../types/kanban';

const KanbanBoard: React.FC = () => {
  const [columns, setColumns] = useState<KanbanColumn[]>([]);
  const [cards, setCards] = useState<Record<string, KanbanCard[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<KanbanFilters>({});
  
  const applyBoardData = useCallback(
    (data: { columns?: KanbanColumn[]; cards?: Record<string, KanbanCard[]> }) => {
      setColumns(data.columns ?? []);
      setCards(data.cards ?? {});
    },
    []
  );

  const fetchBoardData = useCallback(
    async (overrideFilters?: KanbanFilters) => {
      try {
        setLoading(true);
        setError(null);

        const effectiveFilters = overrideFilters ?? filters;
        const data = await kanbanService.getBoardData(effectiveFilters);
        applyBoardData(data);
      } catch (err) {
        console.error('Error fetching kanban board:', err);
        setError('Не удалось загрузить данные канбан-доски. Попробуйте обновить страницу.');
      } finally {
        setLoading(false);
      }
    },
    [applyBoardData, filters]
  );
  
  // Initial data fetch
  useEffect(() => {
    fetchBoardData();
  }, [fetchBoardData]);

  // Refetch data when filters change
  useEffect(() => {
    if (searchQuery.trim()) {
      return;
    }

    const timeoutId = setTimeout(() => {
      fetchBoardData();
    }, 400);

    return () => clearTimeout(timeoutId);
  }, [filters, searchQuery, fetchBoardData]);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!searchQuery.trim()) {
        fetchBoardData();
        return;
      }

      fetchBoardData({ ...filters, clientName: searchQuery });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, filters, fetchBoardData]);
  
  const sortedColumns = useMemo(
    () => [...columns].sort((a, b) => a.order - b.order),
    [columns]
  );

  const formatTime = useCallback((value?: string) => {
    if (!value) {
      return '—';
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return '—';
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }, []);
  
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
    
    const cardId = Number(draggableId);

    const originalCards = Object.fromEntries(
      Object.entries(cards).map(([key, value]) => [key, value.map(card => ({ ...card }))])
    );

    setCards(prevCards => {
      const draft = Object.fromEntries(
        Object.entries(prevCards).map(([key, value]) => [key, [...value]])
      );

      const fromColumn = draft[source.droppableId] ?? [];
      const [movedCard] = fromColumn.splice(source.index, 1);
      if (!movedCard) {
        return prevCards;
      }

      const toColumn = draft[destination.droppableId] ?? [];
      const updatedCard: KanbanCard = {
        ...movedCard,
        column_id: destination.droppableId,
        state: destination.droppableId,
      };
      toColumn.splice(destination.index, 0, updatedCard);

      draft[source.droppableId] = fromColumn;
      draft[destination.droppableId] = toColumn;
      return draft;
    });

    try {
      const currentEmployee = authService.getCurrentUser();
      await kanbanService.moveCard(cardId, {
        to_column_id: destination.droppableId,
        employee_id: currentEmployee?.id,
      });
      await fetchBoardData();
    } catch (err) {
      console.error('Error moving card:', err);
      setCards(originalCards);
      setError('Не удалось переместить карточку. Попробуйте ещё раз.');
      setTimeout(() => setError(null), 3000);
    }
  };
  
  if (loading && Object.keys(cards).length === 0) {
    return <div className="flex justify-center items-center h-64">Загрузка канбан-доски…</div>;
  }

  return (
    <div className="p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Управление бронированиями</h1>

        <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-4">
          <div className="relative w-full md:w-64">
            <input
              type="text"
              placeholder="Поиск по клиенту или референсу"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <svg className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <select
            value={filters.state || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, state: e.target.value || undefined }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Все статусы</option>
            <option value="draft">Черновик</option>
            <option value="pending">Новые</option>
            <option value="confirmed">Подтверждённые</option>
            <option value="in_progress">В процессе</option>
            <option value="completed">Завершённые</option>
            <option value="cancelled">Отменённые</option>
            <option value="no_show">Неявка</option>
            <option value="rescheduled">Перенесённые</option>
          </select>

          <select
            value={filters.spaceType || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, spaceType: e.target.value || undefined }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Все площадки</option>
            <option value="studio_a">Студия A</option>
            <option value="studio_b">Студия B</option>
            <option value="studio_c">Студия C</option>
            <option value="outdoor">Outdoor</option>
            <option value="meeting_room">Переговорная</option>
          </select>

          <div className="flex gap-2">
            <button
              onClick={() => {
                setFilters({});
                setSearchQuery('');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Сбросить фильтры
            </button>
            <button
              onClick={() => fetchBoardData(searchQuery.trim() ? { ...filters, clientName: searchQuery } : undefined)}
              className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
              disabled={loading}
            >
              Обновить
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
          {sortedColumns.map(column => (
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
                            <div className="text-sm text-gray-600">{card.client_name}</div>
                            <div className="text-xs text-gray-500">
                              {formatTime(card.start_time)} – {formatTime(card.end_time)}
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