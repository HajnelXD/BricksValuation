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
    class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
    role="article"
    tabindex="0"
    @click="handleClick"
    @keydown="handleKeydown"
  >
    <!-- Header: Number + Status Badge -->
    <div class="flex items-start justify-between mb-2">
      <h3 class="text-lg font-semibold text-gray-900">{{ item.number }}</h3>
      <span class="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
        {{ item.productionStatusLabel }}
      </span>
    </div>

    <!-- Attributes Icons -->
    <div class="flex flex-wrap gap-2 mb-3">
      <span v-if="item.hasInstructions" title="Ma instrukcje" class="text-lg">
        📘
      </span>
      <span v-if="item.hasBox" title="Ma pudełko" class="text-lg">
        📦
      </span>
      <span v-if="item.isFactorySealed" title="Zapieczętowany" class="text-lg">
        🔒
      </span>
    </div>

    <!-- Statistics -->
    <div class="space-y-1 text-sm text-gray-600 mb-3">
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
    <TopValuationSnippet
      v-if="item.topValuation"
      :valuation="item.topValuation"
    />

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
