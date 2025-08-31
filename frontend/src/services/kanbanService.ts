import { KanbanColumn, KanbanCard, MoveCardRequest } from '../types/kanban';

const API_BASE_URL = '/api/v2';

export class KanbanService {
  static async getKanbanBoard(): Promise<{ columns: KanbanColumn[]; cards: Record<string, KanbanCard[]> }> {
    const response = await fetch(`${API_BASE_URL}/kanban/board`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch kanban board: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getKanbanColumns(): Promise<KanbanColumn[]> {
    const response = await fetch(`${API_BASE_URL}/kanban/columns`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch kanban columns: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getColumnCards(columnId: string): Promise<KanbanCard[]> {
    const response = await fetch(`${API_BASE_URL}/kanban/columns/${columnId}/cards`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch cards for column ${columnId}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async moveCard(cardId: number, moveRequest: MoveCardRequest): Promise<KanbanCard> {
    const response = await fetch(`${API_BASE_URL}/kanban/cards/${cardId}/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(moveRequest),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to move card: ${response.statusText}`);
    }
    
    return response.json();
  }
}