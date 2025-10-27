<script setup lang="ts">
/**
 * BaseButton Component
 * Reusable button component with loading state, multiple variants, and accessibility features
 * Features:
 * - Multiple variants: primary, secondary, danger
 * - Loading state with spinner icon
 * - Disabled state handling
 * - Full width option
 * - Accessible with proper aria labels and focus management
 */

defineProps<{
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
}>();

defineEmits<{
  click: [event: MouseEvent];
}>();

// Variant styles mapping
const variantStyles = {
  primary:
    'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-blue-400 dark:bg-blue-700 dark:hover:bg-blue-600 dark:disabled:bg-blue-900',
  secondary:
    'bg-gray-200 hover:bg-gray-300 text-gray-900 disabled:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white dark:disabled:bg-gray-800',
  danger:
    'bg-red-600 hover:bg-red-700 text-white disabled:bg-red-400 dark:bg-red-700 dark:hover:bg-red-600 dark:disabled:bg-red-900',
};

const selectedVariant = (variant?: string) => {
  return variantStyles[variant as keyof typeof variantStyles] || variantStyles.primary;
};
</script>

<template>
  <button
    :type="type || 'button'"
    :disabled="disabled || loading"
    :class="[
      'px-4 py-2.5 rounded-lg font-semibold transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-blue-500 dark:focus:ring-blue-400',
      'disabled:opacity-60 disabled:cursor-not-allowed',
      'flex items-center justify-center gap-2',
      fullWidth ? 'w-full' : '',
      'text-sm sm:text-base',
      selectedVariant(variant),
    ]"
    :aria-busy="loading"
  >
    <!-- Spinner Icon -->
    <svg
      v-if="loading"
      class="w-4 h-4 animate-spin flex-shrink-0"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>

    <!-- Button Content -->
    <slot />
  </button>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  svg {
    animation: none !important;
  }
}
</style>
