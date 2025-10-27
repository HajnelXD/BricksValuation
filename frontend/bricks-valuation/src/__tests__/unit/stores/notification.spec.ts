import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useNotificationStore } from '@/stores/notification';

describe('Notification Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  describe('addNotification', () => {
    it('should add a notification', () => {
      const store = useNotificationStore();

      const id = store.addNotification('Test message', 'info');

      expect(store.notifications).toHaveLength(1);
      expect(store.notifications[0].message).toBe('Test message');
      expect(store.notifications[0].type).toBe('info');
      expect(id).toBeTruthy();
    });

    it('should return unique notification ids', () => {
      const store = useNotificationStore();

      const id1 = store.addNotification('Message 1', 'info');
      const id2 = store.addNotification('Message 2', 'info');

      expect(id1).not.toBe(id2);
    });

    it('should use default type as info', () => {
      const store = useNotificationStore();

      store.addNotification('Test message');

      expect(store.notifications[0].type).toBe('info');
    });

    it('should use default duration as 5000ms', () => {
      const store = useNotificationStore();

      store.addNotification('Test message');

      expect(store.notifications[0].duration).toBe(5000);
    });

    it('should auto-dismiss notification after duration', () => {
      const store = useNotificationStore();

      store.addNotification('Test message', 'info', 1000);

      expect(store.notifications).toHaveLength(1);

      vi.advanceTimersByTime(1000);

      expect(store.notifications).toHaveLength(0);
    });

    it('should not auto-dismiss if duration is 0', () => {
      const store = useNotificationStore();

      store.addNotification('Test message', 'info', 0);

      vi.advanceTimersByTime(10000);

      expect(store.notifications).toHaveLength(1);
    });
  });

  describe('removeNotification', () => {
    it('should remove notification by id', () => {
      const store = useNotificationStore();

      const id = store.addNotification('Test message', 'info', 0);

      expect(store.notifications).toHaveLength(1);

      store.removeNotification(id);

      expect(store.notifications).toHaveLength(0);
    });

    it('should not remove wrong notification', () => {
      const store = useNotificationStore();

      store.addNotification('Message 1', 'info', 0);
      store.addNotification('Message 2', 'info', 0);

      store.removeNotification('wrong-id');

      expect(store.notifications).toHaveLength(2);
    });
  });

  describe('clearNotifications', () => {
    it('should clear all notifications', () => {
      const store = useNotificationStore();

      store.addNotification('Message 1', 'info', 0);
      store.addNotification('Message 2', 'error', 0);
      store.addNotification('Message 3', 'success', 0);

      expect(store.notifications).toHaveLength(3);

      store.clearNotifications();

      expect(store.notifications).toHaveLength(0);
    });
  });

  describe('Shortcut methods', () => {
    it('should add success notification', () => {
      const store = useNotificationStore();

      store.success('Success message');

      expect(store.notifications[0].type).toBe('success');
      expect(store.notifications[0].message).toBe('Success message');
    });

    it('should add error notification', () => {
      const store = useNotificationStore();

      store.error('Error message');

      expect(store.notifications[0].type).toBe('error');
      expect(store.notifications[0].message).toBe('Error message');
    });

    it('should add warning notification', () => {
      const store = useNotificationStore();

      store.warning('Warning message');

      expect(store.notifications[0].type).toBe('warning');
      expect(store.notifications[0].message).toBe('Warning message');
    });

    it('should add info notification', () => {
      const store = useNotificationStore();

      store.info('Info message');

      expect(store.notifications[0].type).toBe('info');
      expect(store.notifications[0].message).toBe('Info message');
    });

    it('should accept custom duration in shortcut methods', () => {
      const store = useNotificationStore();

      store.success('Message', 3000);

      expect(store.notifications[0].duration).toBe(3000);
    });
  });

  describe('Multiple notifications', () => {
    it('should handle multiple notifications', () => {
      const store = useNotificationStore();

      store.success('Success 1');
      store.error('Error 1');
      store.warning('Warning 1');
      store.info('Info 1');

      expect(store.notifications).toHaveLength(4);
    });

    it('should maintain notification order', () => {
      const store = useNotificationStore();

      store.addNotification('First', 'info', 0);
      store.addNotification('Second', 'info', 0);
      store.addNotification('Third', 'info', 0);

      expect(store.notifications[0].message).toBe('First');
      expect(store.notifications[1].message).toBe('Second');
      expect(store.notifications[2].message).toBe('Third');
    });
  });
});
