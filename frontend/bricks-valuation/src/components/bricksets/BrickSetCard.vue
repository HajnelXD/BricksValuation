<script setup lang="ts">
/**
 * BrickSetCard Component
 * Displays a single BrickSet in list view
 * Handles click/keyboard navigation and displays all relevant information
 */

import type { BrickSetListItemViewModel } from '@/types/bricksets';
import TopValuationSnippet from './TopValuationSnippet.vue';

const props = defineProps<{
  item: BrickSetListItemViewModel;
}>();

const emit = defineEmits<{
  click: [id: number];
}>();

function handleClick() {
  emit('click', props.item.id);
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    emit('click', props.item.id);
  }
}
</script>

<template>
  <li
    class="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:shadow-lg hover:border-gray-600 transition-all cursor-pointer"
    role="article"
    tabindex="0"
    @click="handleClick"
    @keydown="handleKeydown"
  >
    <!-- Header: Number + Status Badges -->
    <div class="flex items-start justify-between mb-2">
      <h3 class="text-lg font-semibold text-white">{{ item.number }}</h3>
      <div class="flex gap-2 flex-wrap">
        <span
          class="inline-block px-2 py-1 bg-blue-900 text-blue-300 text-xs font-medium rounded border border-blue-700"
        >
          {{ item.productionStatusLabel }}
        </span>
        <span
          class="inline-block px-2 py-1 bg-green-900 text-green-300 text-xs font-medium rounded border border-green-700"
        >
          {{ item.completenessLabel }}
        </span>
      </div>
    </div>

    <!-- Attributes Icons -->
    <div class="flex flex-wrap gap-2 mb-3">
      <span
        v-if="item.hasInstructions"
        :title="$t('bricksets.card.instructionsTitle')"
        class="text-lg"
      >
        📘
      </span>
      <span v-if="item.hasBox" :title="$t('bricksets.card.boxTitle')" class="text-lg"> 📦 </span>
      <span v-if="item.isFactorySealed" :title="$t('bricksets.card.sealedTitle')" class="text-lg">
        🔒
      </span>
    </div>

    <!-- Statistics -->
    <div class="space-y-1 text-sm text-gray-400 mb-3">
      <p>
        💰 {{ item.valuationsCount }}
        {{ $t('bricksets.valuations') }}
      </p>
      <p>
        ❤️ {{ item.totalLikes }}
        {{ $t('bricksets.likes') }}
      </p>
    </div>

    <!-- Top Valuation Snippet -->
    <TopValuationSnippet v-if="item.topValuation" :valuation="item.topValuation" />

    <!-- Timestamp -->
    <p class="text-xs text-gray-500 mt-3">{{ item.createdAtRelative }}</p>
  </li>
</template>

<style scoped>
li {
  transition: all 0.2s ease-in-out;
}

li:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
