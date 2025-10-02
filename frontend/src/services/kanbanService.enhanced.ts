/**
 * Enhanced Kanban Service
 * Comprehensive API client for Kanban board operations
 */

import { KanbanColumn, KanbanCard, MoveCardRequest } from '../types/kanban';
import api from './api';

export interface KanbanBoardData {
  columns: KanbanColumn[];
  cards: Record<string, KanbanCard[]>;
}

export interface KanbanFilters {
  dateFrom?: string;
  dateTo?: string;
  clientName?: string;
  state?: string;
  spaceType?: string;
}

class KanbanService {
  private buildParams(filters?: KanbanFilters): Record<string, string> {
    const params: Record<string, string> = {};
    if (!filters) {
      return params;
    }

    Object.entries(filters).forEach(([key, value]) => {
      if (!value) return;

      switch (key) {
        case 'dateFrom':
          params['date_from'] = value;
          break;
        case 'dateTo':
          params['date_to'] = value;
          break;
        case 'clientName':
          params['client_name'] = value;
          break;
        case 'spaceType':
          params['space_type'] = value;
          break;
        default:
          params[key] = value;
      }
    });
    return params;
  }

  async getBoardData(filters?: KanbanFilters): Promise<KanbanBoardData> {
    try {
      const { data } = await api.get<KanbanBoardData>('/kanban/board', {
        params: this.buildParams(filters),
      });
      return data;
    } catch (error) {
      console.error('Failed to fetch Kanban board data:', error);
      throw new Error(`Unable to load board data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getColumns(): Promise<KanbanColumn[]> {
    const { data } = await api.get<KanbanColumn[]>('/kanban/columns');
    return data;
  }

  async getColumnCards(columnId: string, filters?: KanbanFilters): Promise<KanbanCard[]> {
    const { data } = await api.get<KanbanCard[]>(`/kanban/columns/${columnId}/cards`, {
      params: this.buildParams(filters),
    });
    return data;
  }

  async moveCard(cardId: number, moveRequest: MoveCardRequest): Promise<KanbanCard> {
    try {
      const { data } = await api.post<KanbanCard>(`/kanban/cards/${cardId}/move`, moveRequest);
      return data;
    } catch (error) {
      console.error(`Failed to move card ${cardId}:`, error);
      throw new Error(`Unable to move card: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getCard(cardId: number): Promise<KanbanCard> {
    const { data } = await api.get<KanbanCard>(`/kanban/cards/${cardId}`);
    return data;
  }

  async updateCard(cardId: number, updates: Partial<KanbanCard>): Promise<KanbanCard> {
    const { data } = await api.patch<KanbanCard>(`/kanban/cards/${cardId}`, updates);
    return data;
  }

  async deleteCard(cardId: number): Promise<void> {
    await api.delete(`/kanban/cards/${cardId}`);
  }

  async batchMoveCards(moves: Array<{ cardId: number; moveRequest: MoveCardRequest }>): Promise<KanbanCard[]> {
    const { data } = await api.post<KanbanCard[]>('/kanban/cards/batch-move', { moves });
    return data;
  }

  async createColumn(column: Omit<KanbanColumn, 'id'>): Promise<KanbanColumn> {
    const { data } = await api.post<KanbanColumn>('/kanban/columns', column);
    return data;
  }

  async updateColumn(columnId: string, updates: Partial<KanbanColumn>): Promise<KanbanColumn> {
    const { data } = await api.patch<KanbanColumn>(`/kanban/columns/${columnId}`, updates);
    return data;
  }

  async deleteColumn(columnId: string): Promise<void> {
    await api.delete(`/kanban/columns/${columnId}`);
  }

  async reorderColumns(columnOrders: Array<{ id: string; order: number }>): Promise<KanbanColumn[]> {
    const { data } = await api.post<KanbanColumn[]>('/kanban/columns/reorder', { columnOrders });
    return data;
  }

  async getBoardStats(dateFrom?: string, dateTo?: string): Promise<{
    totalCards: number;
    cardsByColumn: Record<string, number>;
    averageTimeInColumn: Record<string, number>;
    revenueByColumn: Record<string, number>;
  }> {
    const params: Record<string, string> = {};
    if (dateFrom) params.dateFrom = dateFrom;
    if (dateTo) params.dateTo = dateTo;
    const { data } = await api.get('/kanban/stats', { params });
    return data;
  }

  async searchCards(query: string, filters?: KanbanFilters): Promise<KanbanCard[]> {
    if (!query.trim()) {
      return [];
    }

    const board = await this.getBoardData({ ...filters, clientName: query });
    return Object.values(board.cards || {}).flat();
  }
}

// Export singleton instance
export const kanbanService = new KanbanService();

export default kanbanService;
