<script setup lang="ts">
/**
 * EmptyState Component
 * Displays when no results match the current filters
 */
</script>

<template>
  <div
    data-testid="empty-state"
    class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center"
  >
    <p class="text-gray-600">
      {{ $t('bricksets.noResults') }}
    </p>
    <p class="text-gray-500 text-sm mt-2">
      {{ $t('bricksets.tryAdjustingFilters') }}
    </p>
  </div>
</template>

<style scoped></style>
