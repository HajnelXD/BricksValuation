/**
 * Notification Store
 * Manages toast notifications and alerts
 * Uses Pinia store with setup syntax
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number; // in milliseconds, 0 = no auto-dismiss
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([]);
  let notificationId = 0;

  /**
   * Add a new notification (toast)
   * @param message - notification message
   * @param type - notification type (success, error, warning, info)
   * @param duration - auto-dismiss duration in ms (default 5000), 0 = no auto-dismiss
   * @returns notification id
   */
  function addNotification(
    message: string,
    type: 'success' | 'error' | 'warning' | 'info' = 'info',
    duration = 5000
  ): string {
    const id = `notification-${notificationId++}`;
    const notification: Notification = {
      id,
      message,
      type,
      duration,
    };

    notifications.value.push(notification);

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  }

  /**
   * Remove a notification by id
   */
  function removeNotification(id: string): void {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const index = notifications.value.findIndex((n: any) => n.id === id);
    if (index >= 0) {
      notifications.value.splice(index, 1);
    }
  }

  /**
   * Clear all notifications
   */
  function clearNotifications(): void {
    notifications.value = [];
  }

  /**
   * Shortcut methods for common notification types
   */
  function success(message: string, duration = 5000): string {
    return addNotification(message, 'success', duration);
  }

  function error(message: string, duration = 5000): string {
    return addNotification(message, 'error', duration);
  }

  function warning(message: string, duration = 5000): string {
    return addNotification(message, 'warning', duration);
  }

  function info(message: string, duration = 5000): string {
    return addNotification(message, 'info', duration);
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    success,
    error,
    warning,
    info,
  };
});
