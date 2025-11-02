<script setup lang="ts">
/**
 * LikeButton Component
 * Przycisk lajku z licznikiem i dynamiczną ikoną serca
 *
 * Features:
 * - Filled heart when already liked, outline when not
 * - Disabled state for author or when not authenticated
 * - Loading spinner during API request
 * - Responsive styling with dark mode support
 * - Accessibility features (aria-label, aria-busy)
 *
 * Props:
 * - likesCount: Current number of likes
 * - disabled: Whether button should be disabled
 * - loading: Whether API request is in progress
 * - isLiked: Whether current user has liked (optional, defaults to false)
 */

defineProps<{
  likesCount: number;
  disabled: boolean;
  loading: boolean;
  isLiked?: boolean;
}>();

const emit = defineEmits<{
  like: [];
}>();

function handleClick() {
  emit('like');
}
</script>

<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :class="[
      'flex items-center gap-2 px-3 py-2 rounded-lg font-semibold transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-red-500',
      disabled
        ? 'bg-gray-700 text-gray-400 cursor-not-allowed dark:bg-gray-800 dark:text-gray-500'
        : isLiked
          ? 'bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600',
      loading ? 'opacity-70' : '',
    ]"
    :aria-busy="loading"
    :aria-label="
      disabled
        ? $t('likes.button.loginToLike')
        : isLiked
          ? $t('likes.button.liked')
          : $t('likes.button.like')
    "
    @click="handleClick"
  >
    <!-- Spinner when loading -->
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

    <!-- Heart Icon: Filled when liked, outline when not -->
    <span class="text-lg flex-shrink-0" aria-hidden="true">
      {{ isLiked ? '❤️' : '🤍' }}
    </span>

    <!-- Count -->
    <span class="min-w-[1.5rem] text-center">{{ likesCount }}</span>
  </button>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  svg {
    animation: none !important;
  }
}
</style>
