import { ENV } from '../config/env';

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private isConnected = false;

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      // Use the same base URL as the API but with ws protocol
      const wsUrl = ENV.API_URL.replace('http', 'ws') + '/ws/notifications';
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('WebSocket connected to notifications channel');
        this.isConnected = true;
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.attemptReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnected = false;
      };
    } catch (error) {
      console.error('Error establishing WebSocket connection:', error);
      this.attemptReconnect();
    }
  }

  private handleMessage(data: any) {
    console.log('Received WebSocket message:', data);
    
    // Notify all listeners for this event type
    if (data.type && this.listeners.has(data.type)) {
      const listeners = this.listeners.get(data.type);
      if (listeners) {
        listeners.forEach(listener => {
          try {
            listener(data);
          } catch (error) {
            console.error('Error in WebSocket listener:', error);
          }
        });
      }
    }
    
    // Also notify general message listeners
    if (this.listeners.has('message')) {
      const listeners = this.listeners.get('message');
      if (listeners) {
        listeners.forEach(listener => {
          try {
            listener(data);
          } catch (error) {
            console.error('Error in WebSocket listener:', error);
          }
        });
      }
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('Max WebSocket reconnection attempts reached');
    }
  }

  subscribe(eventType: string, callback: (data: any) => void) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    
    this.listeners.get(eventType)?.add(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(callback);
      }
    };
  }

  sendMessage(message: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.listeners.clear();
    this.isConnected = false;
  }

  isConnectedStatus(): boolean {
    return this.isConnected;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();