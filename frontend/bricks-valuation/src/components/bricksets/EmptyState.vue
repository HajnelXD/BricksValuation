<script setup lang="ts">
/**
 * EmptyState Component
 * Displays when no results match the current filters
 */

defineEmits<{
  'reset-filters': [];
}>();
</script>

<template>
  <div data-testid="empty-state" class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
    <p class="text-gray-600 mb-4">
      {{ $t('bricksets.noResults') }}
    </p>
    <button
      @click="$emit('reset-filters')"
      class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
    >
      {{ $t('bricksets.clearFilters') }}
    </button>
  </div>
</template>

<style scoped></style>
