<script setup lang="ts">
/**
 * AuthFormLayout Component
 * Provides consistent layout for authentication forms (register, login, password reset)
 * Features:
 * - Centered, responsive container (mobile-first)
 * - Proper spacing and max-width constraints
 * - Dark mode support
 * - Accessible structure with semantic HTML
 */

defineProps<{
  title?: string;
}>();
</script>

<template>
  <div
    class="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 py-8 sm:px-6 lg:px-8 transition-colors duration-200"
  >
    <div class="w-full max-w-sm sm:max-w-md space-y-6 sm:space-y-8">
      <!-- Header -->
      <div class="text-center">
        <h1 v-if="title" class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          {{ title }}
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          <slot name="subtitle" />
        </p>
      </div>

      <!-- Form Slot -->
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-md sm:shadow-lg p-6 sm:p-8 border border-gray-200 dark:border-gray-700"
      >
        <slot />
      </div>

      <!-- Links Slot (e.g., "Already have an account? Login") -->
      <div class="text-center text-sm text-gray-600 dark:text-gray-400">
        <slot name="links" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Smooth color transitions for dark mode */
@media (prefers-color-scheme: dark) {
  div {
    transition-property: background-color, border-color;
    transition-duration: 200ms;
  }
}

/* Accessibility: Reduce motion preferences */
@media (prefers-reduced-motion: reduce) {
  div {
    transition: none !important;
  }
}
</style>
