<script setup lang="ts">
/**
 * OwnedBrickSetCard Component
 * Displays a card for a user's own brickset in My BrickSets view
 * Shows: number, status, metrics, and edit indicator
 */

import type { OwnedBrickSetViewModel } from '@/types/bricksets';
import BrickSetBasicInfo from './BrickSetBasicInfo.vue';
import BrickSetMetrics from './BrickSetMetrics.vue';
import EditableIndicator from './EditableIndicator.vue';

const props = defineProps<{
  brickset: OwnedBrickSetViewModel;
}>();

const emit = defineEmits<{
  'card-click': [id: number];
  'edit-click': [id: number];
}>();

function handleCardClick() {
  emit('card-click', props.brickset.id);
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    emit('card-click', props.brickset.id);
  }
}

function handleEditClick() {
  emit('edit-click', props.brickset.id);
}
</script>

<template>
  <div
    class="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:shadow-lg hover:border-gray-600 transition-all cursor-pointer"
    role="article"
    tabindex="0"
    @click="handleCardClick"
    @keydown="handleKeydown"
  >
    <!-- Header with Number and Badges -->
    <BrickSetBasicInfo :brickset="brickset" />

    <!-- Metrics -->
    <BrickSetMetrics :valuations-count="brickset.valuationsCount" :total-likes="brickset.totalLikes" />

    <!-- Footer with Edit Button -->
    <div class="flex items-center justify-end">
      <EditableIndicator :editable="brickset.editable" @edit-click="handleEditClick" />
    </div>
  </div>
</template>

<style scoped>
div {
  transition: all 0.2s ease-in-out;
}

div:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
