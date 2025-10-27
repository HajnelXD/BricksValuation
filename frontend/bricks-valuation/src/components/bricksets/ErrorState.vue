<script setup lang="ts">
/**
 * ErrorState Component
 * Displays when API call fails
 */

defineProps<{
  error: string | null;
}>();

defineEmits<{
  retry: [];
}>();
</script>

<template>
  <div data-testid="error-state" class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
    <p class="text-red-800 mb-3">{{ error || 'Nieznany błąd' }}</p>
    <button
      @click="$emit('retry')"
      data-testid="retry-button"
      class="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
    >
      {{ $t('common.retry') }}
    </button>
  </div>
</template>

<style scoped></style>
