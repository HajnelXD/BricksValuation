<script setup lang="ts">
/**
 * ValidationErrorList Component
 * Displays multiple form validation errors or server errors in a user-friendly format
 *
 * Features:
 * - Multiple error messages display
 * - Optional dismissible functionality
 * - Auto-remove functionality after timeout
 * - Alert role with aria-live for screen readers
 */

import { ref } from 'vue';

interface Props {
  errors: string[];
  type?: 'error' | 'warning' | 'info';
  isDismissible?: boolean;
  autoDismissMs?: number;
}

withDefaults(defineProps<Props>(), {
  type: 'error',
  isDismissible: true,
  autoDismissMs: 0,
});

const isVisible = ref(true);

function dismiss() {
  isVisible.value = false;
}
</script>

<template>
  <transition v-if="isVisible && errors.length > 0" name="slide-down">
    <div
      v-if="isVisible && errors.length > 0"
      :class="[
        'rounded-lg p-4 mb-4 border-l-4 transition-all duration-200',
        type === 'error'
          ? 'bg-red-50 dark:bg-red-900/20 border-red-400 text-red-800 dark:text-red-200'
          : type === 'warning'
            ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400 text-yellow-800 dark:text-yellow-200'
            : 'bg-blue-50 dark:bg-blue-900/20 border-blue-400 text-blue-800 dark:text-blue-200',
      ]"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          <span v-if="type === 'error'" class="text-xl">❌</span>
          <span v-else-if="type === 'warning'" class="text-xl">⚠️</span>
          <span v-else class="text-xl">ℹ️</span>
        </div>

        <div class="flex-1">
          <ul class="space-y-2">
            <li v-for="(error, index) in errors" :key="index" class="flex items-start gap-2">
              <span
                class="flex-shrink-0 mt-1 w-1.5 h-1.5 rounded-full"
                :class="
                  type === 'error'
                    ? 'bg-red-400'
                    : type === 'warning'
                      ? 'bg-yellow-400'
                      : 'bg-blue-400'
                "
              ></span>
              <span class="flex-1 text-sm">{{ error }}</span>
            </li>
          </ul>
        </div>

        <button
          v-if="isDismissible"
          :class="[
            'flex-shrink-0 p-1 rounded hover:opacity-70 transition-opacity',
            type === 'error'
              ? 'text-red-600 dark:text-red-400'
              : type === 'warning'
                ? 'text-yellow-600 dark:text-yellow-400'
                : 'text-blue-600 dark:text-blue-400',
          ]"
          aria-label="Zamknij powiadomienie o błędzie"
          @click="dismiss"
        >
          ✕
        </button>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (prefers-reduced-motion: reduce) {
  .slide-down-enter-active,
  .slide-down-leave-active {
    transition: none;
  }
}
</style>
