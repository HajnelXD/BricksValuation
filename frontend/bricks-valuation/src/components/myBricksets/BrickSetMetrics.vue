<script setup lang="ts">
/**
 * BrickSetMetrics Component
 * Displays key metrics about a brickset:
 * - Number of valuations (with clipboard icon)
 * - Number of likes (with heart icon)
 */

interface Props {
  valuationsCount: number;
  totalLikes: number;
}

defineProps<Props>();
</script>

<template>
  <div class="flex gap-4 text-sm text-gray-400 mb-3">
    <!-- Valuations Metric -->
    <div class="flex items-center gap-2">
      <span>📋</span>
      <span>{{ valuationsCount }} {{ $t('myBrickSets.metrics.valuations') }}</span>
    </div>

    <!-- Likes Metric -->
    <div class="flex items-center gap-2">
      <span>❤️</span>
      <span>{{ totalLikes }} {{ $t('myBrickSets.metrics.likes') }}</span>
    </div>
  </div>
</template>

<style scoped></style>
