/**
 * Enhanced Kanban Service
 * Comprehensive API client for Kanban board operations
 */

import { KanbanColumn, KanbanCard, MoveCardRequest } from '../types/kanban';
import authService from './authService';

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
  private baseUrl = '/api';
  
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = authService.getToken();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
  
  /**
   * Get complete Kanban board data
   */
  async getBoardData(filters?: KanbanFilters): Promise<KanbanBoardData> {
    try {
      const queryParams = new URLSearchParams();
      
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) queryParams.append(key, value);
        });
      }
      
      const query = queryParams.toString();
      const endpoint = `/kanban/board${query ? `?${query}` : ''}`;
      
      return await this.makeRequest<KanbanBoardData>(endpoint);
    } catch (error) {
      console.error('Failed to fetch Kanban board data:', error);
      throw new Error(`Unable to load board data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
  
  /**
   * Get all Kanban columns
   */
  async getColumns(): Promise<KanbanColumn[]> {
    return this.makeRequest<KanbanColumn[]>('/kanban/columns');
  }
  
  /**
   * Get cards for specific column
   */
  async getColumnCards(columnId: string, filters?: KanbanFilters): Promise<KanbanCard[]> {
    const queryParams = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });
    }
    
    const query = queryParams.toString();
    const endpoint = `/kanban/columns/${columnId}/cards${query ? `?${query}` : ''}`;
    
    return this.makeRequest<KanbanCard[]>(endpoint);
  }
  
  /**
   * Move a card to different column
   */
  async moveCard(cardId: number, moveRequest: MoveCardRequest): Promise<KanbanCard> {
    try {
      return await this.makeRequest<KanbanCard>(`/kanban/cards/${cardId}/move`, {
        method: 'POST',
        body: JSON.stringify(moveRequest),
      });
    } catch (error) {
      console.error(`Failed to move card ${cardId}:`, error);
      throw new Error(`Unable to move card: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
  
  /**
   * Get card details
   */
  async getCard(cardId: number): Promise<KanbanCard> {
    return this.makeRequest<KanbanCard>(`/kanban/cards/${cardId}`);
  }
  
  /**
   * Update card details
   */
  async updateCard(cardId: number, updates: Partial<KanbanCard>): Promise<KanbanCard> {
    return this.makeRequest<KanbanCard>(`/kanban/cards/${cardId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }
  
  /**
   * Delete card (cancel booking)
   */
  async deleteCard(cardId: number): Promise<void> {
    return this.makeRequest<void>(`/kanban/cards/${cardId}`, {
      method: 'DELETE',
    });
  }
  
  /**
   * Batch move multiple cards
   */
  async batchMoveCards(moves: Array<{ cardId: number; moveRequest: MoveCardRequest }>): Promise<KanbanCard[]> {
    return this.makeRequest<KanbanCard[]>('/kanban/cards/batch-move', {
      method: 'POST',
      body: JSON.stringify({ moves }),
    });
  }
  
  /**
   * Create new column
   */
  async createColumn(column: Omit<KanbanColumn, 'id'>): Promise<KanbanColumn> {
    return this.makeRequest<KanbanColumn>('/kanban/columns', {
      method: 'POST',
      body: JSON.stringify(column),
    });
  }
  
  /**
   * Update column
   */
  async updateColumn(columnId: string, updates: Partial<KanbanColumn>): Promise<KanbanColumn> {
    return this.makeRequest<KanbanColumn>(`/kanban/columns/${columnId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }
  
  /**
   * Delete column
   */
  async deleteColumn(columnId: string): Promise<void> {
    return this.makeRequest<void>(`/kanban/columns/${columnId}`, {
      method: 'DELETE',
    });
  }
  
  /**
   * Reorder columns
   */
  async reorderColumns(columnOrders: Array<{ id: string; order: number }>): Promise<KanbanColumn[]> {
    return this.makeRequest<KanbanColumn[]>('/kanban/columns/reorder', {
      method: 'POST',
      body: JSON.stringify({ columnOrders }),
    });
  }
  
  /**
   * Get Kanban board statistics
   */
  async getBoardStats(dateFrom?: string, dateTo?: string): Promise<{
    totalCards: number;
    cardsByColumn: Record<string, number>;
    averageTimeInColumn: Record<string, number>;
    revenueByColumn: Record<string, number>;
  }> {
    const queryParams = new URLSearchParams();
    if (dateFrom) queryParams.append('dateFrom', dateFrom);
    if (dateTo) queryParams.append('dateTo', dateTo);
    
    const query = queryParams.toString();
    const endpoint = `/kanban/stats${query ? `?${query}` : ''}`;
    
    return this.makeRequest(endpoint);
  }
  
  /**
   * Search cards across all columns
   */
  async searchCards(query: string, filters?: KanbanFilters): Promise<KanbanCard[]> {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append('q', query);
      
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) queryParams.append(key, value);
        });
      }
      
      const searchQuery = queryParams.toString();
      return await this.makeRequest<KanbanCard[]>(`/kanban/search?${searchQuery}`);
    } catch (error) {
      console.error(`Failed to search cards with query "${query}":`, error);
      throw new Error(`Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

// Export singleton instance
export const kanbanService = new KanbanService();

export default kanbanService;
