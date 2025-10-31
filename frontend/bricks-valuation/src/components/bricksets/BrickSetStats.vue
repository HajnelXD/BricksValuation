<script setup lang="ts">
/**
 * BrickSetStats Component
 * Statystyki zestawu prezentowane jako metryki
 */

import type { BrickSetStatsViewModel } from '@/types/bricksets';

defineProps<{
  stats: BrickSetStatsViewModel;
}>();
</script>

<template>
  <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-4">
    <div class="flex gap-6 flex-wrap justify-center sm:justify-start">
      <div class="text-center sm:text-left">
        <p class="text-gray-400 text-sm mb-1">{{ $t('bricksets.valuations') }}</p>
        <p class="text-2xl font-bold text-white">💰 {{ stats.valuationsCount }}</p>
      </div>
      <div class="text-center sm:text-left">
        <p class="text-gray-400 text-sm mb-1">{{ $t('bricksets.likes') }}</p>
        <p class="text-2xl font-bold text-white">❤️ {{ stats.totalLikes }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
