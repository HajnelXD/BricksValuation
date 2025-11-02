<script setup lang="ts">
/**
 * BrickSetBasicInfo Component
 * Displays basic information about a brickset:
 * - Number (formatted)
 * - Production status badge
 * - Completeness badge
 */

import type { OwnedBrickSetViewModel } from '@/types/bricksets';

defineProps<{
  brickset: OwnedBrickSetViewModel;
}>();
</script>

<template>
  <div class="flex items-start justify-between gap-3 mb-3">
    <!-- Number -->
    <span class="text-lg font-semibold text-white">{{ brickset.number }}</span>

    <!-- Status Badges -->
    <div class="flex gap-2 flex-wrap">
      <!-- Production Status Badge -->
      <span
        class="inline-block px-2 py-1 text-xs font-medium rounded border"
        :class="
          brickset.productionStatusLabel === $t('myBrickSets.productionStatus.active')
            ? 'bg-blue-900 text-blue-300 border-blue-700'
            : 'bg-red-900 text-red-300 border-red-700'
        "
      >
        {{ brickset.productionStatusLabel }}
      </span>

      <!-- Completeness Badge -->
      <span
        class="inline-block px-2 py-1 text-xs font-medium rounded border"
        :class="
          brickset.completenessLabel === $t('myBrickSets.completeness.complete')
            ? 'bg-green-900 text-green-300 border-green-700'
            : 'bg-yellow-900 text-yellow-300 border-yellow-700'
        "
      >
        {{ brickset.completenessLabel }}
      </span>
    </div>
  </div>
</template>

<style scoped></style>
