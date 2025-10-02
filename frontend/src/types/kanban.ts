export interface KanbanColumn {
  id: string;
  title: string;
  order: number;
  color: string;
}

export interface KanbanCard {
  id: number;
  reference: string;
  title: string;
  client_name: string;
  start_time: string;
  end_time: string;
  state: string;
  column_id: string;
}

export interface MoveCardRequest {
  to_column_id: string;
  employee_id?: number;
}