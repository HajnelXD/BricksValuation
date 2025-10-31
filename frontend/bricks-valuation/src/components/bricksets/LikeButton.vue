<script setup lang="ts">
/**
 * LikeButton Component
 * Przycisk lajku z licznikiem, disabled jeśli użytkownik jest autorem lub już polajkował
 */

defineProps<{
  likesCount: number;
  disabled: boolean;
  loading: boolean;
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
      'flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-blue-500',
      disabled
        ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
        : 'bg-blue-600 hover:bg-blue-700 text-white',
      loading ? 'opacity-60' : '',
    ]"
    :aria-busy="loading"
    :aria-label="disabled ? $t('bricksets.detail.liked') : $t('bricksets.detail.likeButton')"
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

    <!-- Heart Icon -->
    <span class="text-lg" aria-hidden="true">❤️</span>

    <!-- Count -->
    <span>{{ likesCount }}</span>

    <!-- Text -->
    <span v-if="disabled && !loading" class="text-sm">{{ $t('bricksets.detail.liked') }}</span>
    <span v-else-if="!loading" class="text-sm">{{ $t('bricksets.detail.likeButton') }}</span>
  </button>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  svg {
    animation: none !important;
  }
}
</style>
