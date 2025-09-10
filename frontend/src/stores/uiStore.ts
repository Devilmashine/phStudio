/**
 * UI Store
 * Zustand store для управления UI состоянием
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { UIStoreState, Notification, NotificationAction } from './types';

interface UIStoreActions {
  // Theme
  toggleDarkMode: () => void;
  setDarkMode: (enabled: boolean) => void;
  
  // Layout
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Notifications
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Modals
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;
  toggleModal: (modalId: string) => void;
  closeAllModals: () => void;
  
  // Loading states
  setGlobalLoading: (loading: boolean) => void;
  
  // WebSocket connection
  setWSConnected: (connected: boolean) => void;
  setWSReconnecting: (reconnecting: boolean) => void;
  
  // Utility methods
  showSuccess: (message: string, title?: string) => void;
  showError: (message: string, title?: string) => void;
  showWarning: (message: string, title?: string) => void;
  showInfo: (message: string, title?: string) => void;
}

type UIStore = UIStoreState & UIStoreActions;

const initialState: UIStoreState = {
  // Theme
  darkMode: false,
  
  // Layout
  sidebarCollapsed: false,
  
  // Notifications
  notifications: [],
  
  // Modals
  modals: {},
  
  // Loading states
  globalLoading: false,
  
  // Real-time connection
  wsConnected: false,
  wsReconnecting: false,
};

// Helper function to generate unique IDs
const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export const useUIStore = create<UIStore>()(
  devtools(
    immer(
      persist(
        (set, get) => ({
          ...initialState,

          // Theme
          toggleDarkMode: () => {
            set((state) => {
              state.darkMode = !state.darkMode;
            });
          },

          setDarkMode: (enabled: boolean) => {
            set((state) => {
              state.darkMode = enabled;
            });
          },

          // Layout
          toggleSidebar: () => {
            set((state) => {
              state.sidebarCollapsed = !state.sidebarCollapsed;
            });
          },

          setSidebarCollapsed: (collapsed: boolean) => {
            set((state) => {
              state.sidebarCollapsed = collapsed;
            });
          },

          // Notifications
          addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
            set((state) => {
              const newNotification: Notification = {
                ...notification,
                id: generateId(),
                timestamp: Date.now(),
                read: false,
              };
              
              state.notifications.unshift(newNotification);
              
              // Keep only last 50 notifications
              if (state.notifications.length > 50) {
                state.notifications = state.notifications.slice(0, 50);
              }
            });
          },

          markNotificationRead: (id: string) => {
            set((state) => {
              const notification = state.notifications.find(n => n.id === id);
              if (notification) {
                notification.read = true;
              }
            });
          },

          markAllNotificationsRead: () => {
            set((state) => {
              state.notifications.forEach(notification => {
                notification.read = true;
              });
            });
          },

          removeNotification: (id: string) => {
            set((state) => {
              state.notifications = state.notifications.filter(n => n.id !== id);
            });
          },

          clearNotifications: () => {
            set((state) => {
              state.notifications = [];
            });
          },

          // Modals
          openModal: (modalId: string) => {
            set((state) => {
              state.modals[modalId] = true;
            });
          },

          closeModal: (modalId: string) => {
            set((state) => {
              state.modals[modalId] = false;
            });
          },

          toggleModal: (modalId: string) => {
            set((state) => {
              state.modals[modalId] = !state.modals[modalId];
            });
          },

          closeAllModals: () => {
            set((state) => {
              Object.keys(state.modals).forEach(modalId => {
                state.modals[modalId] = false;
              });
            });
          },

          // Loading states
          setGlobalLoading: (loading: boolean) => {
            set((state) => {
              state.globalLoading = loading;
            });
          },

          // WebSocket connection
          setWSConnected: (connected: boolean) => {
            set((state) => {
              state.wsConnected = connected;
              if (connected) {
                state.wsReconnecting = false;
              }
            });
          },

          setWSReconnecting: (reconnecting: boolean) => {
            set((state) => {
              state.wsReconnecting = reconnecting;
            });
          },

          // Utility methods
          showSuccess: (message: string, title?: string) => {
            get().addNotification({
              type: 'success',
              title: title || 'Успех',
              message,
            });
          },

          showError: (message: string, title?: string) => {
            get().addNotification({
              type: 'error',
              title: title || 'Ошибка',
              message,
            });
          },

          showWarning: (message: string, title?: string) => {
            get().addNotification({
              type: 'warning',
              title: title || 'Предупреждение',
              message,
            });
          },

          showInfo: (message: string, title?: string) => {
            get().addNotification({
              type: 'info',
              title: title || 'Информация',
              message,
            });
          },
        }),
        {
          name: 'ui-store',
          partialize: (state) => ({
            darkMode: state.darkMode,
            sidebarCollapsed: state.sidebarCollapsed,
          }),
        }
      )
    ),
    { name: 'UIStore' }
  )
);

export default useUIStore;
