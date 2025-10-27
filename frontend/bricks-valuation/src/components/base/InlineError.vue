<script setup lang="ts">
/**
 * InlineError Component
 * Displays server error messages with accessibility features (alert role, aria-live)
 * Features:
 * - Alert role for screen readers
 * - Optional dismissible button
 * - Smooth fade-in animation
 * - Red styling for error state
 */

defineProps<{
  message: string;
  dismissible?: boolean;
}>();

defineEmits<{
  dismiss: [];
}>();
</script>

<template>
  <div
    v-if="message"
    role="alert"
    aria-live="assertive"
    class="flex items-start gap-3 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 animate-in fade-in duration-200"
  >
    <!-- Warning Icon -->
    <span class="flex-shrink-0 text-lg leading-none">⚠️</span>

    <!-- Error Message -->
    <div class="flex-1">
      <p class="text-sm text-red-700 dark:text-red-400 leading-tight">{{ message }}</p>
    </div>

    <!-- Dismiss Button (optional) -->
    <button
      v-if="dismissible"
      type="button"
      class="flex-shrink-0 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
      aria-label="Zamknij komunikat błędu"
      @click="$emit('dismiss')"
    >
      ✕
    </button>
  </div>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  div {
    animation: none !important;
  }
}
</style>
