import { useState, useEffect, useRef } from 'react';

interface WebSocketHook {
  lastMessage: string | null;
  sendMessage: (message: string) => void;
  readyState: number;
}

export const useWebSocket = (url: string | null): WebSocketHook => {
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Don't connect if no URL is provided
    if (!url) {
      setReadyState(WebSocket.CLOSED);
      return;
    }

    // Create WebSocket connection
    ws.current = new WebSocket(url);
    
    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setReadyState(WebSocket.OPEN);
    };
    
    ws.current.onmessage = (event) => {
      setLastMessage(event.data);
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setReadyState(WebSocket.CLOSED);
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setReadyState(WebSocket.CLOSED);
    };
    
    // Clean up function
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const sendMessage = (message: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(message);
    } else {
      console.warn('WebSocket is not open. Message not sent:', message);
    }
  };

  return {
    lastMessage,
    sendMessage,
    readyState
  };
};