/**
 * Enhanced WebSocket Service
 * Интеграция с backend Event Bus для real-time обновлений
 */

import { useUIStore, useBookingStore, useEmployeeStore } from '../../stores';
import {
  DomainEvent,
  BookingCreatedEvent,
  BookingStateChangedEvent,
  BookingUpdatedEvent,
  BookingCancelledEvent
} from '../../stores/types';

interface WebSocketConfig {
  url: string;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

class EnhancedWebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private eventHandlers: Map<string, ((event: DomainEvent) => void)[]> = new Map();
  private isConnecting = false;
  private isManualClose = false;

  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = {
      url: config.url || this.getWebSocketUrl(),
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 5,
      heartbeatInterval: config.heartbeatInterval || 30000,
    };

    this.setupEventHandlers();
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/api/v2/ws/kanban`;
  }

  private setupEventHandlers(): void {
    // Setup default event handlers for store updates
    this.subscribe('BOOKING_CREATED', this.handleBookingCreated.bind(this));
    this.subscribe('BOOKING_UPDATED', this.handleBookingUpdated.bind(this));
    this.subscribe('BOOKING_STATE_CHANGED', this.handleBookingStateChanged.bind(this));
    this.subscribe('BOOKING_CANCELLED', this.handleBookingCancelled.bind(this));
  }

  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || this.ws?.readyState === WebSocket.CONNECTING) {
        return;
      }

      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.isConnecting = true;
      this.isManualClose = false;

      try {
        this.ws = new WebSocket(this.config.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          
          const uiStore = useUIStore.getState();
          uiStore.setWSConnected(true);
          uiStore.setWSReconnecting(false);
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          
          const uiStore = useUIStore.getState();
          uiStore.setWSConnected(false);

          if (!this.isManualClose) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          
          const uiStore = useUIStore.getState();
          uiStore.setWSConnected(false);
          
          if (this.reconnectAttempts === 0) {
            reject(error);
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  public disconnect(): void {
    this.isManualClose = true;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }

    const uiStore = useUIStore.getState();
    uiStore.setWSConnected(false);
    uiStore.setWSReconnecting(false);
  }

  private scheduleReconnect(): void {
    if (this.isManualClose || this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached or manual close');
      return;
    }

    this.reconnectAttempts++;
    
    const uiStore = useUIStore.getState();
    uiStore.setWSReconnecting(true);

    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts}`);

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnect failed:', error);
      });
    }, this.config.reconnectInterval * this.reconnectAttempts);
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);

      // Handle pong response
      if (data.type === 'pong') {
        return;
      }

      // Handle domain events
      if (data.event_type) {
        this.handleDomainEvent(data as DomainEvent);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleDomainEvent(event: DomainEvent): void {
    console.log('Received domain event:', event);

    // Notify UI store about event
    const uiStore = useUIStore.getState();
    uiStore.addNotification({
      type: 'info',
      title: 'Обновление',
      message: this.getEventMessage(event),
    });

    // Call registered event handlers
    const handlers = this.eventHandlers.get(event.event_type) || [];
    handlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error(`Error in event handler for ${event.event_type}:`, error);
      }
    });
  }

  private getEventMessage(event: DomainEvent): string {
    switch (event.event_type) {
      case 'BOOKING_CREATED':
        return 'Создано новое бронирование';
      case 'BOOKING_UPDATED':
        return 'Бронирование обновлено';
      case 'BOOKING_STATE_CHANGED':
        return 'Изменен статус бронирования';
      case 'BOOKING_CANCELLED':
        return 'Бронирование отменено';
      default:
        return 'Получено обновление';
    }
  }

  // Event handlers for store updates
  private handleBookingCreated(event: BookingCreatedEvent): void {
    const bookingStore = useBookingStore.getState();
    bookingStore.refreshBookings();
  }

  private handleBookingUpdated(event: BookingUpdatedEvent): void {
    const bookingStore = useBookingStore.getState();
    bookingStore.fetchBooking(event.booking_id);
  }

  private handleBookingStateChanged(event: BookingStateChangedEvent): void {
    const bookingStore = useBookingStore.getState();
    bookingStore.fetchBooking(event.booking_id);
  }

  private handleBookingCancelled(event: BookingCancelledEvent): void {
    const bookingStore = useBookingStore.getState();
    bookingStore.fetchBooking(event.booking_id);
  }

  // Public API for subscribing to events
  public subscribe(eventType: string, handler: (event: DomainEvent) => void): () => void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }

    const handlers = this.eventHandlers.get(eventType)!;
    handlers.push(handler);

    // Return unsubscribe function
    return () => {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }

  // Send message to server
  public send(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  // Get connection status
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'DISCONNECTED';
      default:
        return 'UNKNOWN';
    }
  }
}

// Export singleton instance
export const enhancedWebSocketService = new EnhancedWebSocketService();
export default enhancedWebSocketService;
