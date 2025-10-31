<script setup lang="ts">
/**
 * BrickSetHeader Component
 * Nagłówek zestawu prezentujący numer, statusy i podstawowe atrybuty
 */

import type { BrickSetHeaderViewModel } from '@/types/bricksets';

defineProps<{
  header: BrickSetHeaderViewModel;
}>();
</script>

<template>
  <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-4">
    <!-- Header with number and badges -->
    <div class="flex items-start justify-between mb-4 flex-wrap gap-3">
      <h1 class="text-3xl font-bold text-white">{{ header.number }}</h1>
      <div class="flex gap-2 flex-wrap">
        <span
          class="inline-block px-3 py-1 bg-blue-900 text-blue-300 text-sm font-medium rounded border border-blue-700"
        >
          {{ header.productionStatusLabel }}
        </span>
        <span
          class="inline-block px-3 py-1 bg-green-900 text-green-300 text-sm font-medium rounded border border-green-700"
        >
          {{ header.completenessLabel }}
        </span>
      </div>
    </div>

    <!-- Attributes Icons -->
    <div class="flex flex-wrap gap-3 mb-4">
      <span
        v-if="header.hasInstructions"
        :title="$t('bricksets.card.instructionsTitle')"
        class="text-2xl"
        aria-label="Ma instrukcje"
      >
        📘
      </span>
      <span
        v-if="header.hasBox"
        :title="$t('bricksets.card.boxTitle')"
        class="text-2xl"
        aria-label="Ma pudełko"
      >
        📦
      </span>
      <span
        v-if="header.isFactorySealed"
        :title="$t('bricksets.card.sealedTitle')"
        class="text-2xl"
        aria-label="Zapieczętowany fabrycznie"
      >
        🔒
      </span>
    </div>

    <!-- Owner Initial Estimate -->
    <div v-if="header.ownerInitialEstimate !== null" class="mb-3">
      <p class="text-gray-400 text-sm">
        {{ $t('bricksets.detail.ownerEstimate') }}:
        <span class="text-white font-semibold">{{ header.ownerInitialEstimate }} PLN</span>
      </p>
    </div>

    <!-- Created At -->
    <p class="text-xs text-gray-500">
      {{ $t('bricksets.detail.created') }}: {{ header.createdAtRelative }}
    </p>
  </div>
</template>

<style scoped></style>
