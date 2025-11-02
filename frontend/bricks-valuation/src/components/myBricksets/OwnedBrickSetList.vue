<script setup lang="ts">
/**
 * OwnedBrickSetList Component
 * Container for displaying list of user's bricksets or empty state
 * Uses grid layout for responsive display
 */

import type { OwnedBrickSetViewModel } from '@/types/bricksets';
import OwnedBrickSetCard from './OwnedBrickSetCard.vue';
import EmptyState from './EmptyState.vue';
import LoadingSkeletons from '../bricksets/LoadingSkeletons.vue';

interface Props {
  bricksets: OwnedBrickSetViewModel[];
  isLoading: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  'card-click': [id: number];
  'edit-click': [id: number];
}>();
</script>

<template>
  <!-- Loading State -->
  <LoadingSkeletons v-if="isLoading" :count="3" />

  <!-- Empty State -->
  <div v-else-if="bricksets.length === 0">
    <EmptyState />
  </div>

  <!-- List of Cards -->
  <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <OwnedBrickSetCard
      v-for="brickset in bricksets"
      :key="brickset.id"
      :brickset="brickset"
      @card-click="emit('card-click', $event)"
      @edit-click="emit('edit-click', $event)"
    />
  </div>
</template>

<style scoped></style>
