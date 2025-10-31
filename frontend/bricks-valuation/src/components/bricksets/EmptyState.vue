<script setup lang="ts">
/**
 * EmptyState Component
 * Displays when no results match the current filters
 */
</script>

<template>
  <div
    data-testid="empty-state"
    class="bg-gray-800 border-2 border-dashed border-gray-700 rounded-lg p-12 text-center"
  >
    <p class="text-gray-300">
      {{ $t('bricksets.noResults') }}
    </p>
    <p class="text-gray-400 text-sm mt-2">
      {{ $t('bricksets.tryAdjustingFilters') }}
    </p>
  </div>
</template>

<style scoped></style>
