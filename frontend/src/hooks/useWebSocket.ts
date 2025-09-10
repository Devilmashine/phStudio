/**
 * useWebSocket Hook
 * React hook для работы с enhanced WebSocket service
 */

import { useEffect, useCallback, useRef } from 'react';
import { useUIStore } from '../stores';
import { enhancedWebSocketService } from '../services/websocket/enhancedWebSocketService';
import { DomainEvent } from '../stores/types';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (event: DomainEvent) => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    autoConnect = true,
    onConnect,
    onDisconnect,
    onError,
    onMessage
  } = options;

  const { wsConnected, wsReconnecting } = useUIStore();
  const callbacksRef = useRef({ onConnect, onDisconnect, onError, onMessage });

  // Update callbacks ref when they change
  useEffect(() => {
    callbacksRef.current = { onConnect, onDisconnect, onError, onMessage };
  }, [onConnect, onDisconnect, onError, onMessage]);

  // Auto connect/disconnect
  useEffect(() => {
    if (autoConnect && !wsConnected && !wsReconnecting) {
      enhancedWebSocketService.connect()
        .then(() => {
          callbacksRef.current.onConnect?.();
        })
        .catch((error) => {
          callbacksRef.current.onError?.(error);
        });
    }

    return () => {
      if (autoConnect) {
        enhancedWebSocketService.disconnect();
        callbacksRef.current.onDisconnect?.();
      }
    };
  }, [autoConnect, wsConnected, wsReconnecting]);

  // Subscribe to specific events
  const subscribe = useCallback((eventType: string, handler: (event: DomainEvent) => void) => {
    return enhancedWebSocketService.subscribe(eventType, handler);
  }, []);

  // Send message
  const send = useCallback((message: any) => {
    enhancedWebSocketService.send(message);
  }, []);

  // Manual connect
  const connect = useCallback(async () => {
    try {
      await enhancedWebSocketService.connect();
      callbacksRef.current.onConnect?.();
    } catch (error) {
      callbacksRef.current.onError?.(error as Event);
      throw error;
    }
  }, []);

  // Manual disconnect
  const disconnect = useCallback(() => {
    enhancedWebSocketService.disconnect();
    callbacksRef.current.onDisconnect?.();
  }, []);

  return {
    isConnected: wsConnected,
    isReconnecting: wsReconnecting,
    connectionState: enhancedWebSocketService.getConnectionState(),
    subscribe,
    send,
    connect,
    disconnect,
  };
};

// Specialized hooks for different event types
export const useBookingEvents = (options: {
  onBookingCreated?: (event: any) => void;
  onBookingUpdated?: (event: any) => void;
  onBookingStateChanged?: (event: any) => void;
  onBookingCancelled?: (event: any) => void;
} = {}) => {
  const { subscribe } = useWebSocket({ autoConnect: true });

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (options.onBookingCreated) {
      unsubscribers.push(subscribe('BOOKING_CREATED', options.onBookingCreated));
    }

    if (options.onBookingUpdated) {
      unsubscribers.push(subscribe('BOOKING_UPDATED', options.onBookingUpdated));
    }

    if (options.onBookingStateChanged) {
      unsubscribers.push(subscribe('BOOKING_STATE_CHANGED', options.onBookingStateChanged));
    }

    if (options.onBookingCancelled) {
      unsubscribers.push(subscribe('BOOKING_CANCELLED', options.onBookingCancelled));
    }

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [subscribe, options.onBookingCreated, options.onBookingUpdated, options.onBookingStateChanged, options.onBookingCancelled]);
};

export const useEmployeeEvents = (options: {
  onEmployeeCreated?: (event: any) => void;
  onEmployeeUpdated?: (event: any) => void;
  onEmployeeStatusChanged?: (event: any) => void;
} = {}) => {
  const { subscribe } = useWebSocket({ autoConnect: true });

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (options.onEmployeeCreated) {
      unsubscribers.push(subscribe('EMPLOYEE_CREATED', options.onEmployeeCreated));
    }

    if (options.onEmployeeUpdated) {
      unsubscribers.push(subscribe('EMPLOYEE_UPDATED', options.onEmployeeUpdated));
    }

    if (options.onEmployeeStatusChanged) {
      unsubscribers.push(subscribe('EMPLOYEE_STATUS_CHANGED', options.onEmployeeStatusChanged));
    }

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [subscribe, options.onEmployeeCreated, options.onEmployeeUpdated, options.onEmployeeStatusChanged]);
};

export default useWebSocket;