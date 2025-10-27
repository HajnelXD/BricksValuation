<script setup lang="ts">
/**
 * NotificationToaster Component
 * Displays toast notifications from notification store
 * Features:
 * - Auto-dismiss after configured duration
 * - Multiple notifications stacked
 * - Different styles for success, error, warning, info
 * - Smooth animations (fade-in, slide-in)
 * - Dismiss button on each notification
 */

import { computed } from 'vue';
import { useNotificationStore } from '@/stores/notification';

const notificationStore = useNotificationStore();

const notifications = computed(() => notificationStore.notifications);

/**
 * Get background color based on notification type
 */
function getNotificationClasses(type: string): string {
  const baseClasses = 'flex items-center gap-3 px-4 py-3 rounded-lg shadow-md border-l-4 max-w-sm';

  switch (type) {
    case 'success':
      return `${baseClasses} bg-green-50 dark:bg-green-900/20 border-green-500 text-green-800 dark:text-green-200`;
    case 'error':
      return `${baseClasses} bg-red-50 dark:bg-red-900/20 border-red-500 text-red-800 dark:text-red-200`;
    case 'warning':
      return `${baseClasses} bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500 text-yellow-800 dark:text-yellow-200`;
    case 'info':
    default:
      return `${baseClasses} bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-800 dark:text-blue-200`;
  }
}

/**
 * Get icon for notification type
 */
function getIcon(type: string): string {
  switch (type) {
    case 'success':
      return '✓';
    case 'error':
      return '✕';
    case 'warning':
      return '⚠';
    case 'info':
    default:
      return 'ℹ';
  }
}
</script>

<template>
  <div
    class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"
    role="region"
    aria-live="polite"
    aria-label="Notifications"
  >
    <transition-group name="toast" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="getNotificationClasses(notification.type)"
        class="animate-in fade-in slide-in-from-right-4 duration-300 pointer-events-auto"
      >
        <!-- Icon -->
        <span class="flex-shrink-0 text-lg font-bold">
          {{ getIcon(notification.type) }}
        </span>

        <!-- Message -->
        <p class="flex-1 text-sm font-medium">
          {{ notification.message }}
        </p>

        <!-- Dismiss Button -->
        <button
          type="button"
          class="flex-shrink-0 hover:opacity-70 transition-opacity"
          :aria-label="`Close ${notification.type} notification`"
          @click="notificationStore.removeNotification(notification.id)"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 300ms ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.toast-move {
  transition: transform 300ms ease;
}

@media (prefers-reduced-motion: reduce) {
  .toast-enter-active,
  .toast-leave-active,
  .toast-move {
    transition: none !important;
  }
}
</style>
